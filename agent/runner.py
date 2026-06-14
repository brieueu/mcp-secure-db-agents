from __future__ import annotations

from agent.qwen_prompts import build_sql_messages
from agent.tool_router import extract_sql


class AgentRunner:
    def __init__(self, model_client, tools, role: str = "analista"):
        self.model_client = model_client
        self.tools = tools
        self.role = role

    def answer(self, question: str) -> dict:
        schema = self.tools.descrever_esquema_autorizado(self.role)
        messages = build_sql_messages(question, schema)
        sql = extract_sql(self.model_client.complete(messages))
        result = self.tools.executar_consulta_segura(self.role, sql)
        return {"question": question, "sql": sql, **result}
