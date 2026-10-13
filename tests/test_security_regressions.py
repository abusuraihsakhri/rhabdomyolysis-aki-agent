"""Regression tests for audit authenticity, API boundaries and CSV ingestion."""
import csv
import os
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("AUDIT_SECRET_KEY", "test-only-key-for-regressions-2026")
from agents.base import AuditTrail
from agents.api import app
from cli import main, parse_csv_bool
from rhabdomyolysis_aki_agent.cli import parse_csv_bool as legacy_parse_csv_bool


def test_audit_detects_signed_field_tampering():
    trail = AuditTrail(secret_key="signing-key-for-regressions-only-32")
    trail.log("supervisor", "tier", "ACTION", {"result": "ok"})
    trail.log("supervisor", "tier", "ACTION", {"result": "still-ok"})
    assert trail.verify_integrity()
    snapshot = trail.get_trail()
    snapshot[0]["actor"] = "attacker"
    assert trail.verify_integrity()  # returned list is not mutable internal state
    trail.logs[0]["actor"] = "attacker"
    assert not trail.verify_integrity()  # HMAC, not just predecessor links


def test_audit_detects_hash_and_chain_tampering():
    trail = AuditTrail(secret_key="signing-key-for-regressions-only-32")
    trail.log("one", "tier", "ONE", {"a": 1})
    trail.log("two", "tier", "TWO", {"b": 2})
    trail.logs[1]["prev_hash"] = "forged"
    assert not trail.verify_integrity()


@pytest.mark.parametrize("value,expected", [
    ("True", True), ("TRUE", True), ("yes", True), ("1", True),
    ("False", False), ("FALSE", False), ("0", False), ("no", False),
    ("", False), (None, False),
])
def test_csv_booleans(value, expected):
    assert parse_csv_bool(value) is expected
    assert legacy_parse_csv_bool(value) is expected


def test_csv_booleans_reject_unknown_value():
    with pytest.raises(ValueError, match="Invalid CSV boolean"):
        parse_csv_bool("occasionally")


def test_batch_reads_legacy_example_schema_correctly(tmp_path, monkeypatch):
    monkeypatch.setenv("AUDIT_SECRET_KEY", "regression-test-key-of-sufficient-length")
    source = tmp_path / "input.csv"
    dest = tmp_path / "results.csv"
    source.write_text(
        "case_id,patient_synthetic_id,metric_primary,metric_secondary,is_stat,status_flag\n"
        "DEMO-1,SYNTH-1,10,2,False,NOMINAL\n"
        "DEMO-2,SYNTH-2,10,2,True,NOMINAL\n",
        encoding="utf-8",
    )
    assert main(["batch", "--input", str(source), "--output", str(dest)]) == 0
    with dest.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert rows[0]["overall_urgency"] == "ROUTINE"
    assert rows[1]["overall_urgency"] == "CRITICAL_STAT_PANIC"


def test_audit_logs_are_not_public(monkeypatch):
    monkeypatch.setenv("AUDIT_SECRET_KEY", "regression-test-key-of-sufficient-length")
    monkeypatch.setenv("AUDIT_READ_TOKEN", "separate-regression-log-reader-token")
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    assert client.get("/api/audit/logs").status_code == 403
    assert client.get("/api/audit/logs", headers={"X-Audit-Key": "wrong"}).status_code == 403
    assert client.get("/api/audit/logs", headers={"X-Audit-Key": os.environ["AUDIT_READ_TOKEN"]}).status_code == 200


def test_api_rejects_identifier_pattern_in_nested_attributes(monkeypatch):
    monkeypatch.setenv("AUDIT_SECRET_KEY", "regression-test-key-of-sufficient-length")
    payload = {
        "task_id": "DEMO-1", "target_identifier": "SYNTH-1",
        "primary_metric": 10, "attributes": {"email": "jane.doe@example.org"},
    }
    client = TestClient(app)
    response = client.post("/api/audit", json=payload)
    assert response.status_code == 422
    assert "jane.doe@example.org" not in response.text


def test_browser_script_syntax_if_node_available(tmp_path):
    page = Path(__file__).resolve().parents[1] / "web" / "index.html"
    html = page.read_text(encoding="utf-8")
    assert "Not for clinical use" in html
    assert "onclick=" not in html
    script = html.split("<script>", 1)[1].split("</script>", 1)[0]
    script_path = tmp_path / "demo.js"
    script_path.write_text(script, encoding="utf-8")
    try:
        result = subprocess.run(["node", "--check", str(script_path)], capture_output=True, text=True, check=False)
    except FileNotFoundError:
        pytest.skip("Node.js not available")
    assert result.returncode == 0, result.stderr
