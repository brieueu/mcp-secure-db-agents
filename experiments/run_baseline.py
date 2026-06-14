from __future__ import annotations

import argparse
import time


def baseline_record(prompt: str, sql: str, allowed: bool, latency_ms: float, error: str | None = None) -> dict:
    return {"mode": "baseline_direct_sql", "prompt": prompt, "sql": sql, "allowed": allowed, "latency_ms": latency_ms, "error": error}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="Qual categoria de filme teve maior receita?")
    parser.add_argument("--sql", default="SELECT categoria, receita_total FROM vendas_por_categoria LIMIT 5")
    args = parser.parse_args()
    start = time.perf_counter()
    print(baseline_record(args.prompt, args.sql, True, (time.perf_counter() - start) * 1000))


if __name__ == "__main__":
    main()
