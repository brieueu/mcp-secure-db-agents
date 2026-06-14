from pathlib import Path

from mcp_server.policy_engine import PolicyEngine


def test_policy_loads_roles_and_lists_allowed_objects():
    engine = PolicyEngine.from_yaml(Path("policies/roles.yaml"))
    assert "filmes_publicos" in engine.allowed_objects("usuario_comum")
    assert "vendas_por_categoria" in engine.allowed_objects("analista")


def test_policy_authorizes_allowed_tool_and_object():
    engine = PolicyEngine.from_yaml(Path("policies/roles.yaml"))
    decision = engine.authorize("analista", "executar_consulta_segura", {"vendas_por_categoria"})
    assert decision.allowed is True


def test_policy_blocks_forbidden_table_even_for_analyst():
    engine = PolicyEngine.from_yaml(Path("policies/roles.yaml"))
    decision = engine.authorize("analista", "executar_consulta_segura", {"payment"})
    assert decision.allowed is False
    assert "payment" in decision.reason
