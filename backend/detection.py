"""Transparent, explainable detection rules for CyberPulse."""
from __future__ import annotations

from backend import database

SENSITIVE_PATHS = {"/decoy/.env", "/decoy/.git/config", "/decoy/wp-admin"}


def analyse_event(event: dict) -> list[dict]:
    """Evaluate one saved event and return alerts created by the rules."""
    created: list[dict] = []
    source = event["source_ip"]
    simulated = bool(event.get("simulated"))

    if event["event_type"] == "login_attempt":
        attempts = database.recent_login_attempts(source, seconds=60)
        if attempts >= 5:
            alert = database.create_alert(
                source_ip=source,
                severity="HIGH",
                title="Repeated decoy login attempts",
                reason=f"Observed {attempts} login attempts from this source within approximately 60 seconds. This is a suspicious pattern, not proof of a real compromise.",
                event_id=event["id"],
                simulated=simulated,
            )
            if alert:
                created.append(alert)

    if event["path"] in SENSITIVE_PATHS or event["event_type"] == "sensitive_path_probe":
        alert = database.create_alert(
            source_ip=source,
            severity="MEDIUM",
            title="Sensitive-path reconnaissance",
            reason=f"The source requested decoy path {event['path']}. The route is a harmless decoy and returned no secret data.",
            event_id=event["id"],
            simulated=simulated,
        )
        if alert:
            created.append(alert)

    return created
