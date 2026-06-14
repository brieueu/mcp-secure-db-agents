from agent.prompts import SYSTEM_PROMPT


def build_sql_messages(question: str, schema: dict) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Esquema autorizado: {schema}\nPergunta: {question}\nGere apenas SQL SELECT."},
    ]
