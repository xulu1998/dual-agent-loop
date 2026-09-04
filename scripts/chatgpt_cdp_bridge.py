#!/usr/bin/env python3
"""
Chrome DevTools Protocol (CDP) Bridge for ChatGPT / Claude Web Interface.

Enables an autonomous local agent to communicate directly with an external
LLM Project Lead in a Chrome browser tab via WebSocket.

Prerequisites:
    1. Launch Chrome with remote debugging enabled and a dedicated user-data-dir.
       Chrome 136+ does not honor --remote-debugging-port against the default
       Chrome data directory, and using an isolated profile is safer.

       macOS:
         /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\
           --remote-debugging-port=9222 \\
           --user-data-dir="$HOME/.dual-agent-loop/chrome-profile"

       Linux:
         google-chrome \\
           --remote-debugging-port=9222 \\
           --user-data-dir=/tmp/dual-agent-loop-chrome

       Windows PowerShell:
         & "$env:ProgramFiles\\Google\\Chrome\\Application\\chrome.exe" `
           --remote-debugging-port=9222 `
           "--user-data-dir=$env:TEMP\\dual-agent-loop-chrome"

    2. In that isolated Chrome profile, open ChatGPT (https://chatgpt.com)
       or Claude (https://claude.ai) in a tab.
    3. Install dependencies:
       python -m pip install -r requirements.txt

Security:
    CDP is powerful. Use a dedicated browser profile, do not expose the remote
    debugging port to untrusted networks, and only connect trusted local agents.
"""

import argparse
import asyncio
import json
import sys
import time
import urllib.request

try:
    import websockets
except ImportError:
    print(
        "Error: 'websockets' library is required. "
        "Run: python -m pip install websockets",
        file=sys.stderr,
    )
    sys.exit(1)


async def eval_js(ws, js_code: str, msg_id: int = 1):
    """Evaluates JavaScript in the browser context via CDP Runtime.evaluate."""
    msg = {
        "id": msg_id,
        "method": "Runtime.evaluate",
        "params": {
            "expression": js_code,
            "returnByValue": True,
            "awaitPromise": True,
        },
    }
    await ws.send(json.dumps(msg))
    while True:
        resp = await ws.recv()
        res = json.loads(resp)
        if res.get("id") == msg_id:
            if "exceptionDetails" in res.get("result", {}):
                err = res["result"]["exceptionDetails"]
                print(f"[CDP Error] JavaScript exception: {err}", file=sys.stderr)
                return None
            return res.get("result", {}).get("result", {}).get("value")


def find_tab(port: int = 9222, url_pattern: str = "chatgpt.com"):
    """Finds target browser tab matching url_pattern via CDP HTTP endpoint."""
    try:
        req = urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=5)
        tabs = json.loads(req.read().decode("utf-8"))
    except Exception as e:
        print(
            f"[Error] Failed to connect to Chrome at "
            f"http://127.0.0.1:{port}/json/list: {e}",
            file=sys.stderr,
        )
        print(
            "Ensure Chrome is running with --remote-debugging-port=9222 "
            "and a dedicated --user-data-dir.",
            file=sys.stderr,
        )
        return None

    for tab in tabs:
        if url_pattern in tab.get("url", ""):
            return tab

    # Fallback to any active page if pattern not found.
    for tab in tabs:
        if tab.get("type") == "page":
            print(
                f"[Warning] Pattern '{url_pattern}' not found, falling back to tab: "
                f"{tab.get('title')}",
                file=sys.stderr,
            )
            return tab

    return None


async def send_report_and_listen(ws_url: str, report_text: str, timeout_seconds: int = 600):
    """Injects report text into input box, clicks send, and awaits response."""
    async with websockets.connect(ws_url, max_size=32 * 1024 * 1024) as ws:
        print("[CDP] Connected to browser WebSocket debugger.")

        # Step 1: Inject text into ChatGPT / Claude input area.
        inject_script = f"""
        (() => {{
            const el = document.querySelector('#prompt-textarea') ||
                       document.querySelector('[contenteditable="true"]') ||
                       document.querySelector('textarea');
            if (!el) return {{ success: false, error: 'Input field not found' }};

            el.focus();
            if (el.tagName === 'TEXTAREA') {{
                el.value = {json.dumps(report_text)};
                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }} else {{
                document.execCommand('selectAll', false, null);
                document.execCommand('insertText', false, {json.dumps(report_text)});
            }}

            const sendBtn = document.querySelector('button[data-testid="send-button"]') ||
                            document.querySelector('button[aria-label*="Send"]') ||
                            document.querySelector('button[aria-label*="发送"]');

            if (sendBtn && !sendBtn.disabled) {{
                sendBtn.click();
                return {{ success: true, method: 'click_send' }};
            }}

            el.dispatchEvent(new KeyboardEvent('keydown', {{
                key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true
            }}));
            return {{ success: true, method: 'enter_key' }};
        }})()
        """

        result = await eval_js(ws, inject_script, msg_id=10)
        print(f"[CDP] Injection result: {result}")
        if not result or not result.get("success"):
            print("[Error] Failed to inject text into chat prompt area.", file=sys.stderr)
            return None

        print("[CDP] Report delivered. Waiting for Lead response...")
        await asyncio.sleep(4)

        # Step 2: Poll for completion.
        start_time = time.time()
        last_length = 0
        stable_count = 0

        while time.time() - start_time < timeout_seconds:
            status_script = """
            (() => {
                const stopBtn = document.querySelector('button[data-testid="stop-button"]') ||
                                document.querySelector('button[aria-label*="Stop"]') ||
                                document.querySelector('button[aria-label*="停止"]');
                const msgs = document.querySelectorAll('[data-message-author-role="assistant"], .markdown');
                const lastMsg = msgs.length > 0 ? msgs[msgs.length - 1].innerText : "";
                return {
                    isGenerating: !!stopBtn,
                    text: lastMsg,
                    length: lastMsg.length
                };
            })()
            """
            status = await eval_js(ws, status_script, msg_id=20)
            if not status:
                await asyncio.sleep(3)
                continue

            current_len = status.get("length", 0)
            is_gen = status.get("isGenerating", False)

            if is_gen:
                stable_count = 0
                print(
                    f"[CDP] Generating response... ({current_len} chars)",
                    end="\r",
                    flush=True,
                )
            else:
                if current_len > 0 and current_len == last_length:
                    stable_count += 1
                    if stable_count >= 2:
                        print(
                            f"\n[CDP] Generation completed. "
                            f"Total {current_len} characters received."
                        )
                        return status.get("text", "")
                else:
                    stable_count = 0

            last_length = current_len
            await asyncio.sleep(3)

        print("\n[CDP] Timeout waiting for Lead response.", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="CDP Bridge to ChatGPT / Claude")
    parser.add_argument(
        "--port",
        type=int,
        default=9222,
        help="Chrome remote debugging port (default: 9222)",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="chatgpt.com",
        help="URL substring to match target tab",
    )
    parser.add_argument("--file", type=str, help="Path to report markdown file to send")
    parser.add_argument("--message", type=str, help="Direct text message to send")
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Response wait timeout in seconds (default: 600)",
    )

    args = parser.parse_args()

    content = ""
    if args.file:
        with open(args.file, "r", encoding="utf-8") as handle:
            content = handle.read()
    elif args.message:
        content = args.message
    else:
        content = sys.stdin.read()

    if not content.strip():
        print("[Error] No report content provided to send.", file=sys.stderr)
        sys.exit(1)

    tab = find_tab(args.port, args.pattern)
    if not tab:
        sys.exit(1)

    ws_url = tab.get("webSocketDebuggerUrl")
    if not ws_url:
        print("[Error] Target tab does not expose webSocketDebuggerUrl.", file=sys.stderr)
        sys.exit(1)

    response = asyncio.run(
        send_report_and_listen(ws_url, content, timeout_seconds=args.timeout)
    )
    if response:
        print("\n" + "=" * 60)
        print("PROJECT LEAD DIRECTIVE / RESPONSE:")
        print("=" * 60)
        print(response)
        print("=" * 60)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
