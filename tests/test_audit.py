import json

from mcp_server.audit import AuditLogger


def test_audit_logger_writes_jsonl_decision(tmp_path):
    path = tmp_path / "audit.jsonl"
    logger = AuditLogger(path)
    logger.log_decision(role="analista", tool="executar_consulta_segura", allowed=False, reason="blocked", sql="SELECT * FROM payment")
    row = json.loads(path.read_text(encoding="utf-8").strip())
    assert row["role"] == "analista"
    assert row["allowed"] is False
    assert row["reason"] == "blocked"
    assert "timestamp" in row
