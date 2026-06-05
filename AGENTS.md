# AGENTS.md — guidance for AI agents & contributors

This file orients automated agents (and humans) working in this repository. Read it before making
changes. See also `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and `SECURITY.md`.

## What this project is
A self-hostable **FastMCP** server that turns a structured course spec (sent by an AI client via the
Model Context Protocol) into a **self-contained, SCORM-compliant** e-learning package (HTML5 +
`scorm-again` runtime). The server **never calls an LLM** — it only validates, renders, packages, and
runs conformance checks. **Author = the MCP client; assembler = this server.**

## Setup, build, test
```bash
python -m venv .venv && source .venv/bin/activate
pip install ".[dev]"          # add ".[tts]" for the offline Turkish TTS (Piper)
pytest -q                     # full test suite — keep it green
ruff check .                  # lint (CI runs it non-blocking)
```
Optional features need extra tooling and are **skipped** by tests when absent: **video** (Node 22 +
`npm i -g hyperframes` + ffmpeg) and **TTS** (`pip install ".[tts]"` + a Piper voice). A plain
`pip install ".[dev]"` is enough for CI-equivalent checks.

## Repository map
- `core/` — Pydantic models, packaging, storage, manifest, validators (incl. `schema_validate.py`).
- `components/` — HTML renderer + inline runtime engine (`templates.py`) + video compiler.
- `auth/` — API-key + OAuth, SSRF guards, HTML sanitization. **Security-sensitive — do not weaken.**
- `themes/`, `runtime/` — design tokens; vendored SCORM runtime + (validation-only) XSD schemas.
- `server.py` — the `@mcp.tool` endpoints. `tests/` — pytest (+ a Node/vitest harness, when present).

## House rules (important)
- **Additive & backward-compatible.** Do **not** change existing MCP tool signatures or return schemas.
  New behavior is **opt-in**. Heavy/optional features are **lazy** (the "zero-load" contract): nothing
  loads or changes behavior for courses that don't use it.
- **Small, focused modules.** Match the surrounding code's idioms. Turkish inline comments and a
  "Faz N" (phase) convention are used throughout — keep them consistent.
- **Tests first.** Add/adjust tests for any behavior change; the suite must stay green.
- **No secrets, no private infrastructure, no customer data** in code, tests, docs, or commits.
  Only `.env.example` is tracked; real `.env` is gitignored. Reference the connector generically
  (e.g. `http://localhost:8000/mcp`), never a specific hosted deployment.
- **Conformance:** the gating proof of SCORM correctness is a **SCORM Cloud** round-trip (import with
  zero parser errors/warnings + launch + tracking). XSD validation is a supporting check. See
  `docs/CONFORMANCE.md`.

## Definition of done for a change
`pytest -q` green · `ruff check .` clean (or justified) · no secrets/infra added · backward-compatible ·
docs/`CHANGELOG.md` updated when user-facing.
