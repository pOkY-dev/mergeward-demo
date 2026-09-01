# Snapstore

A small self-hosted URL shortener + pastebin API (Flask + SQLite). Two
purposes at once:

1. It's a real, working service — `POST /api/links`, `GET /<slug>` redirect,
   `POST /api/pastes`, `GET /p/<id>`, an API-key-protected admin endpoint,
   and an HMAC-signed deploy webhook. Not a toy single-file script.
2. It's the **testbed repo for [mergeward](../Mergeward/mergeward)** (Р14 in
   mergeward's roadmap: `mergeward` + `mergeward-demo` as two separate
   repos) — real PRs get opened against it to exercise the Action end-to-end,
   instead of throwaway scratch git repos.

## Running it

```bash
pip install -r requirements-dev.txt
python scripts/init_db.py
FLASK_APP=app FLASK_RUN_PORT=5000 flask run
```

## Tests

```bash
pytest
```

## Structure

```
app/
  __init__.py   # Flask app factory
  config.py     # env-based config (no hardcoded secrets)
  routes.py     # HTTP endpoints
  storage.py    # sqlite3 persistence, no ORM
  security.py   # API-key + HMAC webhook auth
  utils.py      # slug/id generation, URL validation
scripts/init_db.py
tests/
```

## Using this repo to test mergeward

`mergeward.yml` at the root configures the Action for this repo (Р17).
`.github/workflows/mergeward.yml` + `.github/workflows/mergeward-resume.yml`
implement the two-workflow HITL pattern (Р6) — **both still reference a
placeholder `OWNER/mergeward@main`** until the `mergeward` repo is actually
published on GitHub; update that once it has a real home.

Planned PR scenarios (mirrors Phase 4 of mergeward's roadmap, run early
here rather than waiting):

| Scenario | Expected outcome |
|---|---|
| Clean feature PR (e.g. a new `/api/links/<slug>/stats` endpoint) | `auto_pass` |
| PR that adds a hardcoded API key/token in `app/config.py` or a script | `auto_block` (gitleaks, CRITICAL) |
| PR that adds a `curl \| sh` step to a deploy script | `needs_review` → HITL, or `auto_block` if LLM gray-zone escalates it |
| PR that adds `eval()`/`subprocess(..., shell=True)` in an ambiguous spot (e.g. a "custom redirect rule" feature) | gray-zone: LLM should distinguish a sanitized use from an unsanitized one |
| PR with an AI co-author trailer, otherwise clean | `auto_pass`, but flagged as AI-authored (Р15) with a tightened review threshold if anything *is* found |

## License

MIT — see [LICENSE](LICENSE).
