"""CyberPulse local honeypot demo app.

Run with: uvicorn backend.main:app --host 127.0.0.1 --port 8000
Do not expose directly to the public internet.
"""
from __future__ import annotations

import secrets
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend import database
from backend.detection import analyse_event

app = FastAPI(title="CyberPulse", version="0.1.0", description="Local educational honeypot monitoring prototype")
FRONTEND = Path(__file__).resolve().parent.parent / "frontend"


@app.on_event("startup")
def startup() -> None:
    database.init_db()


def client_ip(request: Request) -> str:
    # Intentionally do not trust X-Forwarded-For headers in this local demo.
    return request.client.host if request.client else "unknown"


def record(request: Request, *, event_type: str, path: str, severity: str,
           summary: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    event = database.add_event(
        source_ip=client_ip(request), service="HTTP decoy", event_type=event_type,
        path=path, severity=severity, summary=summary, simulated=False, details=details)
    analyse_event(event)
    return event


@app.get("/", response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    file = FRONTEND / "index.html"
    if not file.exists():
        return HTMLResponse("CyberPulse UI file is missing.", status_code=500)
    return HTMLResponse(file.read_text(encoding="utf-8"))


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "application": "CyberPulse", "mode": "local-lab"}


@app.get("/api/summary")
def summary() -> dict[str, int | str]:
    return {
        "total_events": database.count_events(),
        "total_alerts": database.count_alerts(),
        "open_high_alerts": database.count_by_severity("HIGH"),
        "open_medium_alerts": database.count_by_severity("MEDIUM"),
        "status": "ONLINE",
    }


@app.get("/api/events")
def events(limit: int = 100) -> dict[str, Any]:
    return {"items": database.list_events(limit)}


@app.get("/api/alerts")
def alerts(limit: int = 100) -> dict[str, Any]:
    return {"items": database.list_alerts(limit)}


@app.post("/decoy/login")
def decoy_login(request: Request, username: str = Form(default=""), password: str = Form(default="")) -> JSONResponse:
    # Password content is deliberately discarded. Never log or persist it.
    _ = password
    event = record(request, event_type="login_attempt", path="/decoy/login", severity="MEDIUM",
                   summary="Login attempt observed by decoy service",
                   details={"username_supplied": bool(username.strip()), "authentication_performed": False})
    return JSONResponse({"message": "Demo decoy: authentication is disabled.", "event_id": event["id"]}, status_code=401)


@app.get("/decoy/admin")
def decoy_admin(request: Request) -> JSONResponse:
    event = record(request, event_type="admin_path_probe", path="/decoy/admin", severity="LOW",
                   summary="Request observed on decoy admin route")
    return JSONResponse({"message": "Decoy endpoint. No admin interface exists.", "event_id": event["id"]}, status_code=404)


@app.get("/decoy/.env")
def decoy_env(request: Request) -> JSONResponse:
    event = database.add_event(source_ip=client_ip(request), service="HTTP decoy",
        event_type="sensitive_path_probe", path="/decoy/.env", severity="MEDIUM",
        summary="Request for a sensitive-looking decoy path", simulated=False,
        details={"secret_data_returned": False})
    analyse_event(event)
    return JSONResponse({"message": "Decoy endpoint. No file or secrets are served.", "event_id": event["id"]}, status_code=404)


@app.post("/api/demo/run")
def run_demo() -> dict[str, Any]:
    """Insert synthetic events only; never scans or contacts another host."""
    source = "demo-simulator"
    created = []
    for index in range(6):
        event = database.add_event(source_ip=source, service="HTTP decoy", event_type="login_attempt",
            path="/decoy/login", severity="MEDIUM", summary=f"Simulated failed login attempt {index + 1}",
            simulated=True, details={"scenario": "repeated_login", "attempt": index + 1,
                                    "username_supplied": True, "password_stored": False})
        created.append(event)
        analyse_event(event)
    probe = database.add_event(source_ip=source, service="HTTP decoy", event_type="sensitive_path_probe",
        path="/decoy/.env", severity="MEDIUM", summary="Simulated sensitive-path probe", simulated=True,
        details={"scenario": "path_reconnaissance", "secret_data_returned": False})
    created.append(probe)
    analyse_event(probe)
    return {"message": "Synthetic demo events created. No network scanning was performed.", "events_created": len(created)}


@app.post("/api/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: int) -> dict[str, Any]:
    from backend.database import connect
    with connect() as conn:
        cursor = conn.execute("UPDATE alerts SET status='RESOLVED' WHERE id=?", (alert_id,))
        if cursor.rowcount == 0:
            return JSONResponse(status_code=404, content={"detail": "Alert not found"})
    return {"id": alert_id, "status": "RESOLVED"}
