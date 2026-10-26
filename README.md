# CyberPulse

**Detect. Analyse. Defend.**

CyberPulse is a presentation-ready honeypot monitoring prototype. It runs a local decoy HTTP service, records requests as security events, applies transparent rule-based detection, and presents events and alerts in a web dashboard.

> **Safety:** This is a lab/demo project. Bind to `127.0.0.1` by default. Do not expose the service directly to the public internet or use real credentials. It never stores submitted passwords; it records only whether a username field was supplied and the event metadata.

## Features

- Interactive dark dashboard with event counts, severity levels, event stream, and alert explanations.
- Decoy routes (`/decoy/login`, `/decoy/admin`, and `/decoy/.env`) for controlled demonstrations.
- SQLite event and alert storage.
- Detection for repeated login attempts and probing of sensitive-looking paths.
- Demo event generator for safe presentation without external attack traffic.
- Health endpoint and simple JSON API.

## Quick start

Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 in your browser.

To generate safe sample events, use the **Run demo simulation** button in the dashboard. These are explicitly marked as simulated events.

## Project structure

```text
CyberPulse/
├── backend/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, decoy routes, JSON APIs
│   ├── database.py      # SQLite persistence
│   └── detection.py     # Explainable alert rules
├── frontend/
│   └── index.html       # Dashboard UI
├── tests/
│   └── test_detection.py
├── data/                # Runtime SQLite database (gitignored)
├── .gitignore
└── requirements.txt
```

## Architecture

Browser / lab test client → isolated decoy HTTP routes → event logger → SQLite → rule-based detector → dashboard APIs → UI.

The current MVP is an HTTP decoy suitable for local classroom demonstration. It is not an SSH honeypot and should not be represented as one. Cowrie integration can be added later in a separate isolated VM.

## API

- `GET /api/health` — service status
- `GET /api/summary` — event and alert counts
- `GET /api/events?limit=100` — recent events
- `GET /api/alerts?limit=100` — recent alerts
- `POST /api/demo/run` — generate safe, labelled demo events
- `POST /decoy/login` — record a simulated login attempt without saving the password
- `GET /decoy/admin` — record a probe of a decoy admin route
- `GET /decoy/.env` — record a probe of a sensitive-looking decoy path

## Security notes

- Default bind address is localhost only.
- No real authentication is performed by decoy endpoints.
- Submitted passwords are never persisted or logged.
- The demo simulator creates synthetic records and does not scan or contact other systems.
- For any networked lab, use an isolated VM/network and restrictive firewall rules.

## Status

Initial educational MVP; review and test before use beyond a local demo.