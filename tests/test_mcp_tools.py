from mcp_server.audit import AuditLogger
from mcp_server.policy_engine import PolicyEngine
from mcp_server.sql_validator import SQLValidator
from mcp_server.tools import SecureDatabaseTools


class FakeDatabase:
    def __init__(self):
        self.executed = []

    def describe_views(self, objects):
        return {name: [{"column_name": "total", "data_type": "numeric"}] for name in objects}

    def execute_query(self, sql):
        self.executed.append(sql)
        return [{"categoria": "Action", "receita_total": 123.45}]


def build_tools(tmp_path):
    policy = PolicyEngine.from_yaml("policies/roles.yaml")
    validator = SQLValidator()
    audit = AuditLogger(tmp_path / "raw_logs.jsonl")
    return SecureDatabaseTools(FakeDatabase(), policy, validator, audit)


def test_lists_only_allowed_objects_for_role(tmp_path):
    tools = build_tools(tmp_path)
    result = tools.listar_tabelas_permitidas("usuario_comum")
    assert "filmes_publicos" in result["objetos_permitidos"]
    assert "payment" not in result["objetos_permitidos"]


def test_describes_authorized_schema(tmp_path):
    tools = build_tools(tmp_path)
    result = tools.descrever_esquema_autorizado("analista")
    assert "vendas_por_categoria" in result


def test_secure_query_blocks_forbidden_table(tmp_path):
    tools = build_tools(tmp_path)
    result = tools.executar_consulta_segura("analista", "SELECT * FROM payment")
    assert result["allowed"] is False
    assert "payment" in result["reason"]


def test_secure_query_executes_allowed_view(tmp_path):
    tools = build_tools(tmp_path)
    result = tools.executar_consulta_segura("analista", "SELECT categoria, receita_total FROM vendas_por_categoria")
    assert result["allowed"] is True
    assert result["rows"][0]["categoria"] == "Action"
