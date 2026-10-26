"""Small SQLite persistence layer for CyberPulse."""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(os.getenv("CYBERPULSE_DB_PATH", str(Path(__file__).resolve().parent.parent / "data" / "cyberpulse.db")))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source_ip TEXT NOT NULL,
            service TEXT NOT NULL,
            event_type TEXT NOT NULL,
            path TEXT NOT NULL,
            severity TEXT NOT NULL,
            summary TEXT NOT NULL,
            simulated INTEGER NOT NULL DEFAULT 0,
            details_json TEXT NOT NULL DEFAULT '{}'
        );
        CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp DESC);
        CREATE INDEX IF NOT EXISTS idx_events_source_type ON events(source_ip, event_type);
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source_ip TEXT NOT NULL,
            severity TEXT NOT NULL,
            title TEXT NOT NULL,
            reason TEXT NOT NULL,
            event_id INTEGER,
            status TEXT NOT NULL DEFAULT 'OPEN',
            simulated INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(event_id) REFERENCES events(id)
        );
        CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp DESC);
        """)


def add_event(*, source_ip: str, service: str, event_type: str, path: str,
              severity: str, summary: str, simulated: bool = False,
              details: dict[str, Any] | None = None) -> dict[str, Any]:
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO events(timestamp,source_ip,service,event_type,path,severity,summary,simulated,details_json) VALUES(?,?,?,?,?,?,?,?,?)",
            (utc_now(), source_ip, service, event_type, path, severity, summary,
             int(simulated), json.dumps(details or {}, ensure_ascii=True)))
        row = conn.execute("SELECT * FROM events WHERE id=?", (cur.lastrowid,)).fetchone()
        return event_row(row)


def event_row(row: sqlite3.Row) -> dict[str, Any]:
    result = dict(row)
    result["simulated"] = bool(result["simulated"])
    result["details"] = json.loads(result.pop("details_json"))
    return result


def list_events(limit: int = 100) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (max(1, min(limit, 500)),)).fetchall()
        return [event_row(row) for row in rows]


def count_events() -> int:
    with connect() as conn:
        return int(conn.execute("SELECT COUNT(*) FROM events").fetchone()[0])


def create_alert(*, source_ip: str, severity: str, title: str, reason: str,
                 event_id: int | None, simulated: bool = False) -> dict[str, Any] | None:
    with connect() as conn:
        # Avoid flooding the dashboard with identical alerts for the same source.
        existing = conn.execute(
            "SELECT * FROM alerts WHERE source_ip=? AND title=? AND timestamp >= datetime('now','-60 seconds') ORDER BY id DESC LIMIT 1",
            (source_ip, title)).fetchone()
        if existing:
            return None
        cur = conn.execute(
            "INSERT INTO alerts(timestamp,source_ip,severity,title,reason,event_id,simulated) VALUES(?,?,?,?,?,?,?)",
            (utc_now(), source_ip, severity, title, reason, event_id, int(simulated)))
        row = conn.execute("SELECT * FROM alerts WHERE id=?", (cur.lastrowid,)).fetchone()
        result = dict(row)
        result["simulated"] = bool(result["simulated"])
        return result


def list_alerts(limit: int = 100) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (max(1, min(limit, 500)),)).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["simulated"] = bool(item["simulated"])
            result.append(item)
        return result


def count_alerts() -> int:
    with connect() as conn:
        return int(conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0])


def count_by_severity(severity: str) -> int:
    with connect() as conn:
        return int(conn.execute("SELECT COUNT(*) FROM alerts WHERE severity=? AND status='OPEN'", (severity,)).fetchone()[0])


def recent_login_attempts(source_ip: str, seconds: int = 60) -> int:
    with connect() as conn:
        rows = conn.execute(
            "SELECT timestamp FROM events WHERE source_ip=? AND event_type='login_attempt' ORDER BY id DESC LIMIT 50",
            (source_ip,)).fetchall()
    if not rows:
        return 0
    cutoff = datetime.now(timezone.utc).timestamp() - seconds
    total = 0
    for row in rows:
        try:
            value = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00")).timestamp()
        except (ValueError, TypeError):
            continue
        if value >= cutoff:
            total += 1
    return total
