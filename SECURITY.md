# Security

`dual-agent-loop` uses the Chrome DevTools Protocol (CDP) to let a trusted local coding agent communicate with a browser-based Project Lead.

CDP is intentionally powerful. A process attached to an authenticated browser session may be able to inspect page content, interact with the UI, and access information visible to that browser profile.

## Recommended setup

- Use a **dedicated Chrome user-data directory** for `dual-agent-loop`.
- Do **not** attach the bridge to your everyday Chrome profile.
- Keep the Chrome remote-debugging endpoint bound to the local machine.
- Do not expose port `9222` to an untrusted LAN, container network, tunnel, or the public internet.
- Only run local agents, scripts, and dependencies you trust.
- Treat browser cookies, authenticated sessions, chat history, pasted secrets, and page content as sensitive data.
- Close the dedicated browser profile when you are finished using the workflow.

## Chrome 136+

Modern Chrome requires remote debugging to use a non-default user-data directory. Launching an isolated profile is therefore both a compatibility requirement and a useful security boundary.

Example on macOS:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.dual-agent-loop/chrome-profile"
```

Equivalent commands for Linux and Windows are documented in the main README.

## Browser UI automation risk

The bridge currently interacts with browser DOM elements used by ChatGPT / Claude. Those interfaces can change without notice.

If a selector stops matching, the bridge should fail visibly rather than silently claiming that a report was delivered. Review bridge changes carefully, especially changes that broaden selectors or execute additional JavaScript in authenticated pages.

## Reporting a vulnerability

Please do not publish credentials, cookies, private chat content, or other sensitive reproduction data in a public issue.

For non-sensitive hardening requests, selector breakage, or documentation improvements, open a normal GitHub issue with the minimum reproducible details needed to understand the problem.
