# Reprodutibilidade

1. Instale dependências Python em `.venv`.
2. Execute `docker compose up -d` para inicializar PostgreSQL com Sakila.
3. Configure `LOCAL_LLM_BASE_URL` e `LOCAL_LLM_MODEL` para Qwen2.5-Coder local.
4. Rode `pytest -q`.
5. Rode `python -m experiments.run_experiment --limit 5`.
6. Rode `python -m experiments.analyze_results --input results/raw_logs.jsonl`.

A pasta `paper/` é local e ignorada pelo Git.
