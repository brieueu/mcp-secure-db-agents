from agent.runner import AgentRunner


class FakeModel:
    def complete(self, messages):
        return "SELECT categoria, receita_total FROM vendas_por_categoria LIMIT 5"


class FakeTools:
    def __init__(self):
        self.sql = None

    def descrever_esquema_autorizado(self, role):
        return {"vendas_por_categoria": [{"column_name": "categoria", "data_type": "text"}]}

    def executar_consulta_segura(self, role, sql):
        self.sql = sql
        return {"allowed": True, "rows": [{"categoria": "Action", "receita_total": 10}]}


def test_agent_uses_mcp_tools_instead_of_direct_db():
    tools = FakeTools()
    runner = AgentRunner(FakeModel(), tools, role="analista")
    result = runner.answer("Quais categorias tiveram maior receita?")
    assert tools.sql.startswith("SELECT")
    assert result["allowed"] is True
    assert result["rows"][0]["categoria"] == "Action"
