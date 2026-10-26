"""Focused tests for CyberPulse's explainable detection rules."""
from backend.detection import SENSITIVE_PATHS


def test_sensitive_decoy_paths_are_explicit():
    assert "/decoy/.env" in SENSITIVE_PATHS
    assert "/decoy/.git/config" in SENSITIVE_PATHS


def test_normal_path_is_not_sensitive():
    assert "/decoy/home" not in SENSITIVE_PATHS
