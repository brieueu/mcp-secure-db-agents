from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

from mcp_server.audit import AuditLogger
from mcp_server.policy_engine import PolicyEngine
from mcp_server.sql_validator import SQLValidator
from mcp_server.tools import SecureDatabaseTools


class HeuristicDatabase:
    def describe_views(self, objects):
        return {name: [{"column_name": "exemplo", "data_type": "text"}] for name in objects}

    def execute_query(self, sql):
        return [{"categoria": "Action", "receita_total": 100.0, "sql_executado": sql}]


def load_prompts(limit: int | None = None) -> list[dict]:
    rows = []
    for label, path in [
        ("legitimo", Path("experiments/prompts_legitimos.csv")),
        ("sensivel", Path("experiments/prompts_sensiveis.csv")),
        ("malicioso", Path("experiments/prompts_maliciosos.csv")),
    ]:
        with path.open(encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                rows.append({"category": label, **row})
    return rows[:limit] if limit else rows


def heuristic_sql(prompt: str) -> str:
    lower = prompt.lower()
    if "drop" in lower:
        return "DROP TABLE customer"
    if "pg_catalog" in lower or "catálogo" in lower or "catalogo" in lower:
        return "SELECT * FROM pg_catalog.pg_tables"
    if "mês" in lower or "mes" in lower:
        return "SELECT mes, receita_total FROM vendas_por_mes LIMIT 5"
    if "email" in lower or "e-mail" in lower or "endereço" in lower or "endere" in lower:
        return "SELECT * FROM customer LIMIT 5"
    if "histórico individual" in lower or "historico individual" in lower:
        return "SELECT * FROM rental LIMIT 5"
    if "payment" in lower or "pagamento" in lower or "brutos" in lower or "sem usar views" in lower:
        return "SELECT * FROM payment LIMIT 5"
    if "cidade" in lower:
        return "SELECT city, total_clientes FROM clientes_por_cidade LIMIT 5"
    if "alug" in lower:
        return "SELECT title, total_alugueis FROM filmes_mais_alugados LIMIT 5"
    return "SELECT categoria, receita_total FROM vendas_por_categoria LIMIT 5"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--output", default="results/raw_logs.jsonl")
    args = parser.parse_args()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    tools = SecureDatabaseTools(HeuristicDatabase(), PolicyEngine.from_yaml("policies/roles.yaml"), SQLValidator(), AuditLogger(out))
    with out.open("a", encoding="utf-8") as handle:
        for item in load_prompts(args.limit):
            started = time.perf_counter()
            sql = heuristic_sql(item["prompt"])
            result = tools.executar_consulta_segura("analista", sql)
            row = {
                "mode": "secure_mcp",
                "prompt_id": item.get("id"),
                "prompt": item["prompt"],
                "category": item["category"],
                "sql": sql,
                "allowed": result["allowed"],
                "reason": result["reason"],
                "latency_ms": round((time.perf_counter() - started) * 1000, 3),
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
