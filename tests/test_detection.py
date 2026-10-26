"""Focused tests for CyberPulse's explainable detection rules."""
from backend import detection
from backend.detection import SENSITIVE_PATHS


def test_sensitive_decoy_paths_are_explicit():
    assert "/decoy/.env" in SENSITIVE_PATHS
    assert "/decoy/.git/config" in SENSITIVE_PATHS


def test_normal_path_is_not_sensitive():
    assert "/decoy/home" not in SENSITIVE_PATHS


def test_sensitive_path_probe_creates_explained_alert(monkeypatch):
    captured = []
    monkeypatch.setattr(detection.database, "create_alert", lambda **kwargs: captured.append(kwargs) or {"id": 1, **kwargs})
    event = {
        "id": 42,
        "source_ip": "127.0.0.1",
        "event_type": "sensitive_path_probe",
        "path": "/decoy/.env",
        "simulated": True,
    }
    alerts = detection.analyse_event(event)
    assert len(alerts) == 1
    assert captured[0]["severity"] == "MEDIUM"
    assert "no secret data" in captured[0]["reason"]
    assert captured[0]["simulated"] is True


def test_fifth_recent_login_attempt_triggers_high_alert(monkeypatch):
    captured = []
    monkeypatch.setattr(detection.database, "recent_login_attempts", lambda source, seconds=60: 5)
    monkeypatch.setattr(detection.database, "create_alert", lambda **kwargs: captured.append(kwargs) or {"id": 2, **kwargs})
    event = {
        "id": 99,
        "source_ip": "127.0.0.1",
        "event_type": "login_attempt",
        "path": "/decoy/login",
        "simulated": False,
    }
    alerts = detection.analyse_event(event)
    assert len(alerts) == 1
    assert captured[0]["severity"] == "HIGH"
    assert "5 login attempts" in captured[0]["reason"]
