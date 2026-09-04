#!/usr/bin/env python3
"""Experimental CDP transport for a browser-based Project Lead.

This bridge sends one message to a specifically targeted ChatGPT/Claude tab and
returns only a response that appears *after* that send. It intentionally does
not fall back to arbitrary browser pages.

CDP/browser-DOM automation is a pragmatic transport, not a durable protocol.
Use an isolated Chrome profile, keep port 9222 local, and expect selectors to
need maintenance when browser applications change their UI.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
import urllib.request
from urllib.parse import urlparse

try:
    import websockets
except ImportError:
    print(
        "Error: 'websockets' is required. Run: python -m pip install -r requirements.txt",
        file=sys.stderr,
    )
    sys.exit(1)


DEFAULT_ALLOWED_HOSTS = {"chatgpt.com", "claude.ai"}

ADAPTERS = {
    "chatgpt.com": {
        "input": ["#prompt-textarea", 'textarea', '[contenteditable="true"]'],
        "send": [
            'button[data-testid="send-button"]',
            'button[aria-label*="Send"]',
            'button[aria-label*="发送"]',
        ],
        "stop": [
            'button[data-testid="stop-button"]',
            'button[aria-label*="Stop"]',
            'button[aria-label*="停止"]',
        ],
        "assistant": ['[data-message-author-role="assistant"]'],
    },
    "claude.ai": {
        "input": ['[contenteditable="true"]', "textarea"],
        "send": [
            'button[aria-label*="Send"]',
            'button[data-testid="send-button"]',
        ],
        "stop": ['button[aria-label*="Stop"]'],
        # Claude's DOM changes more frequently. These are best-effort defaults;
        # --assistant-selector can override them without editing this file.
        "assistant": [
            '[data-testid="assistant-message"]',
            '.font-claude-message',
        ],
    },
}


def _hostname(url: str) -> str | None:
    try:
        parsed = urlparse(url)
    except ValueError:
        return None
    if parsed.scheme not in {"http", "https"}:
        return None
    return parsed.hostname.lower() if parsed.hostname else None


def _host_matches(url: str, expected_host: str) -> bool:
    """Match an exact host or its subdomains; never use raw substring matching."""
    actual = _hostname(url)
    expected = expected_host.lower().strip(".")
    return bool(actual and (actual == expected or actual.endswith("." + expected)))


def _select_target_tab(tabs, expected_host: str):
    """Return a page on expected_host, or None. Never select an unrelated page."""
    matches = [
        tab
        for tab in tabs
        if tab.get("type") == "page" and _host_matches(tab.get("url", ""), expected_host)
    ]
    if not matches:
        return None

    # Prefer visible-looking pages over extension/devtools pages if metadata exists.
    matches.sort(key=lambda tab: bool(tab.get("webSocketDebuggerUrl")), reverse=True)
    return matches[0]


def find_tab(port: int, expected_host: str):
    """Find a target browser tab via the local CDP HTTP endpoint."""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=5) as response:
            tabs = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        print(
            f"[Error] Cannot reach Chrome at http://127.0.0.1:{port}/json/list: {exc}",
            file=sys.stderr,
        )
        print(
            "Start Chrome with --remote-debugging-port and a dedicated --user-data-dir.",
            file=sys.stderr,
        )
        return None

    tab = _select_target_tab(tabs, expected_host)
    if not tab:
        print(
            f"[Error] No open browser page matched host '{expected_host}'. "
            "The bridge will not fall back to an unrelated tab.",
            file=sys.stderr,
        )
        return None
    return tab


def _adapter_for(host: str, assistant_override: str | None = None):
    adapter = dict(ADAPTERS.get(host, ADAPTERS["chatgpt.com"]))
    adapter = {key: list(value) for key, value in adapter.items()}
    if assistant_override:
        adapter["assistant"] = [assistant_override]
    return adapter


async def eval_js(ws, js_code: str, msg_id: int):
    request = {
        "id": msg_id,
        "method": "Runtime.evaluate",
        "params": {
            "expression": js_code,
            "returnByValue": True,
            "awaitPromise": True,
        },
    }
    await ws.send(json.dumps(request))
    while True:
        response = json.loads(await ws.recv())
        if response.get("id") != msg_id:
            continue
        result = response.get("result", {})
        if "exceptionDetails" in result:
            print(f"[CDP Error] JavaScript exception: {result['exceptionDetails']}", file=sys.stderr)
            return None
        return result.get("result", {}).get("value")


def _snapshot_script(adapter) -> str:
    assistant_selectors = json.dumps(adapter["assistant"])
    stop_selectors = json.dumps(adapter["stop"])
    return f"""
    (() => {{
      const firstSelectorWithNodes = (selectors) => {{
        for (const selector of selectors) {{
          const nodes = Array.from(document.querySelectorAll(selector));
          if (nodes.length) return {{ selector, nodes }};
        }}
        return {{ selector: null, nodes: [] }};
      }};
      const found = firstSelectorWithNodes({assistant_selectors});
      const nodes = found.nodes;
      const last = nodes.length ? nodes[nodes.length - 1] : null;
      const stopVisible = {stop_selectors}.some((s) => document.querySelector(s));
      const text = last ? (last.innerText || last.textContent || "").trim() : "";
      const identity = last ? (
        last.getAttribute("data-message-id") ||
        last.getAttribute("data-testid") ||
        last.id ||
        `${{found.selector || "assistant"}}:${{nodes.length}}:${{text.length}}`
      ) : "";
      return {{
        selector: found.selector,
        assistantCount: nodes.length,
        lastIdentity: identity,
        lastText: text,
        isGenerating: Boolean(stopVisible)
      }};
    }})()
    """


def _send_script(adapter, report_text: str) -> str:
    input_selectors = json.dumps(adapter["input"])
    send_selectors = json.dumps(adapter["send"])
    message_json = json.dumps(report_text)
    return f"""
    (() => {{
      const first = (selectors) => {{
        for (const selector of selectors) {{
          const node = document.querySelector(selector);
          if (node) return node;
        }}
        return null;
      }};
      const el = first({input_selectors});
      if (!el) return {{ success: false, error: "Input field not found" }};

      el.focus();
      if (el.tagName === "TEXTAREA") {{
        const setter = Object.getOwnPropertyDescriptor(
          window.HTMLTextAreaElement.prototype, "value"
        )?.set;
        if (setter) setter.call(el, {message_json});
        else el.value = {message_json};
        el.dispatchEvent(new Event("input", {{ bubbles: true }}));
      }} else {{
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(el);
        selection.removeAllRanges();
        selection.addRange(range);
        document.execCommand("insertText", false, {message_json});
        el.dispatchEvent(new Event("input", {{ bubbles: true }}));
      }}

      const sendButton = first({send_selectors});
      if (!sendButton || sendButton.disabled) {{
        return {{ success: false, error: "Send button not found or disabled" }};
      }}
      sendButton.click();
      return {{ success: true }};
    }})()
    """


def _is_new_response(initial, current) -> bool:
    if not current:
        return False
    if current.get("assistantCount", 0) > initial.get("assistantCount", 0):
        return True
    initial_text = initial.get("lastText", "")
    current_text = current.get("lastText", "")
    if current_text and current_text != initial_text:
        return True
    initial_id = initial.get("lastIdentity", "")
    current_id = current.get("lastIdentity", "")
    return bool(current_id and initial_id and current_id != initial_id)


async def _connect_with_retry(ws_url: str, attempts: int):
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            return await websockets.connect(ws_url, max_size=32 * 1024 * 1024)
        except Exception as exc:
            last_error = exc
            if attempt < attempts:
                await asyncio.sleep(min(attempt, 3))
    raise RuntimeError(f"Could not connect to CDP WebSocket after {attempts} attempts: {last_error}")


async def send_report_and_listen(
    ws_url: str,
    report_text: str,
    adapter,
    *,
    timeout_seconds: int = 600,
    connect_attempts: int = 3,
):
    ws = await _connect_with_retry(ws_url, connect_attempts)
    try:
        print("[CDP] Connected to target browser page.")

        initial = await eval_js(ws, _snapshot_script(adapter), msg_id=10)
        if initial is None:
            print("[Error] Could not capture pre-send assistant snapshot.", file=sys.stderr)
            return None

        sent = await eval_js(ws, _send_script(adapter, report_text), msg_id=20)
        if not sent or not sent.get("success"):
            reason = sent.get("error") if isinstance(sent, dict) else "unknown send failure"
            print(f"[Error] Message was not sent: {reason}", file=sys.stderr)
            return None

        print("[CDP] Message sent. Waiting for a new assistant response...")
        start = time.time()
        response_started = False
        stable_text = None
        stable_count = 0
        poll_id = 100

        while time.time() - start < timeout_seconds:
            current = await eval_js(ws, _snapshot_script(adapter), msg_id=poll_id)
            poll_id += 1
            if not current:
                await asyncio.sleep(2)
                continue

            if not response_started:
                if not _is_new_response(initial, current):
                    await asyncio.sleep(2)
                    continue
                response_started = True
                print("[CDP] New assistant response detected.")

            text = current.get("lastText", "")
            if current.get("isGenerating"):
                stable_count = 0
            elif text:
                if text == stable_text:
                    stable_count += 1
                else:
                    stable_text = text
                    stable_count = 0
                if stable_count >= 2:
                    print(f"[CDP] Response complete ({len(text)} chars).")
                    return text

            await asyncio.sleep(2)

        if not response_started:
            print("[Error] Timed out before any new assistant response appeared.", file=sys.stderr)
        else:
            print("[Error] Timed out while waiting for the new response to stabilize.", file=sys.stderr)
        return None
    finally:
        await ws.close()


def main():
    parser = argparse.ArgumentParser(description="Experimental CDP bridge to a browser Project Lead")
    parser.add_argument("--port", type=int, default=9222, help="Local Chrome CDP port")
    parser.add_argument(
        "--host",
        "--pattern",
        dest="host",
        default="chatgpt.com",
        help="Expected browser hostname (default: chatgpt.com)",
    )
    parser.add_argument(
        "--allow-custom-host",
        action="store_true",
        help="Allow a host outside the built-in chatgpt.com/claude.ai allowlist",
    )
    parser.add_argument(
        "--assistant-selector",
        help="Override the DOM selector used to identify assistant messages",
    )
    parser.add_argument("--file", help="Markdown/text file to send")
    parser.add_argument("--message", help="Direct message to send")
    parser.add_argument("--timeout", type=int, default=600, help="Response timeout seconds")
    parser.add_argument("--connect-attempts", type=int, default=3, help="CDP WebSocket attempts")
    args = parser.parse_args()

    host = args.host.lower().strip(".")
    if host not in DEFAULT_ALLOWED_HOSTS and not args.allow_custom_host:
        print(
            f"[Error] Host '{host}' is not in the default allowlist. "
            "Use --allow-custom-host only when you intentionally trust that target.",
            file=sys.stderr,
        )
        sys.exit(2)

    if args.file:
        with open(args.file, "r", encoding="utf-8") as handle:
            content = handle.read()
    elif args.message:
        content = args.message
    else:
        content = sys.stdin.read()

    if not content.strip():
        print("[Error] No message content provided.", file=sys.stderr)
        sys.exit(2)

    tab = find_tab(args.port, host)
    if not tab:
        sys.exit(1)

    ws_url = tab.get("webSocketDebuggerUrl")
    if not ws_url:
        print("[Error] Target page does not expose webSocketDebuggerUrl.", file=sys.stderr)
        sys.exit(1)

    adapter = _adapter_for(host, args.assistant_selector)
    try:
        response = asyncio.run(
            send_report_and_listen(
                ws_url,
                content,
                adapter,
                timeout_seconds=args.timeout,
                connect_attempts=max(args.connect_attempts, 1),
            )
        )
    except Exception as exc:
        print(f"[Error] Bridge failed: {exc}", file=sys.stderr)
        sys.exit(1)

    if not response:
        sys.exit(1)

    print("\n" + "=" * 64)
    print("PROJECT LEAD RESPONSE")
    print("=" * 64)
    print(response)
    print("=" * 64)


if __name__ == "__main__":
    main()
