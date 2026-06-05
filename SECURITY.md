# Security Policy

## Reporting a vulnerability

Please **do not** open a public issue for security vulnerabilities.

Report privately via one of:
- GitHub **[private vulnerability reporting](../../security/advisories/new)** (preferred), or
- email **security@edumints.com**.

Include a description, steps to reproduce, affected version/commit, and impact if known. We aim to
acknowledge reports within a few business days and will keep you informed of progress.

## Scope notes for self-hosters

This is a self-hostable server. When you deploy it, **you** are responsible for its security posture:

- **Secrets** (API keys, OAuth/IdP credentials) belong in environment variables, never in the repo.
  Only `.env.example` is tracked; real `.env` is gitignored.
- **Network ingress (SSRF):** `add_asset` fetches remote URLs server-side; the project includes SSRF
  guards (internal IPs blocked, redirects re-checked, size/mime limits). Keep them enabled and put the
  server behind appropriate network controls.
- **HTML sanitization:** all `*_html` inputs are sanitized (allowlist). Don't disable it.
- **Resource limits:** the cost guardrails (quotas, TTLs, build timeouts) protect against abuse —
  tune them for your environment.
- **Auth:** the server supports API-key and OAuth flows; protect your endpoint and rotate keys.

## Supported versions

This project is pre-1.0; security fixes target the latest `main`.
