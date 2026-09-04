# Security

`dual-agent-loop` includes an **experimental Chrome DevTools Protocol (CDP) transport** that can let a trusted local coding agent communicate with a browser-based Project Lead.

CDP is powerful. A process attached to an authenticated browser session may inspect page content and interact with UI visible to that browser profile.

## Recommended setup

- Use a **dedicated Chrome user-data directory** for this workflow.
- Do **not** attach the bridge to your everyday Chrome profile.
- Keep the remote-debugging endpoint on the local machine.
- Do not expose port `9222` to an untrusted LAN, container network, tunnel, or public internet.
- Only run agents, scripts, and dependencies you trust.
- Treat cookies, authenticated sessions, chat history, pasted secrets, and page content as sensitive.
- Close the dedicated browser profile when finished.

## Target isolation

The bridge is designed to fail closed:

- it matches an exact requested hostname (or subdomain), not a raw URL substring;
- it does not fall back to an arbitrary open page when the requested service is missing;
- the built-in allowlist is limited to the explicitly supported browser targets unless `--allow-custom-host` is intentionally supplied.

Do not weaken these checks merely to make a broken selector or missing target “work.”

## Response identity

Before sending a message, the bridge captures a snapshot of the current assistant-message state. It only returns a response detected after the send.

This reduces the risk of treating an old answer as a new Project Lead directive, but DOM identity is still application-dependent and should not be treated as a cryptographic message protocol.

## Chrome 136+

Modern Chrome requires remote debugging to use a non-default user-data directory. Example on macOS:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.dual-agent-loop/chrome-profile"
```

Equivalent Linux/Windows commands are in the main README.

## Third-party service policies

Browser automation is not the same thing as an official API integration. Before automating a third-party web service:

- confirm you are authorized to automate the account/service;
- review the applicable service terms and automation policies;
- prefer an approved API, MCP server, or first-party integration when required by that environment.

The workflow/gate model is transport-independent; CDP is not intended to be the only possible transport.

## Browser UI fragility

Chat/web application DOMs can change without notice. Selector breakage should fail visibly rather than silently broadening page access or claiming that a message was delivered.

Use `--assistant-selector` only when you understand the target DOM and intentionally want to override the default response selector.

## Reporting a vulnerability

Do not publish credentials, cookies, private chat content, or other sensitive reproduction data in a public issue.

For non-sensitive hardening requests, selector breakage, parser edge cases, or documentation improvements, open a normal issue with the minimum reproducible details needed to understand the problem.
