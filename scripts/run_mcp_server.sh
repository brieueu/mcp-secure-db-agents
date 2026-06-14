#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/gabriel/Projetos /Agentes LLM em Consultas"
cd "$PROJECT_DIR"

export POLICY_PATH="${POLICY_PATH:-$PROJECT_DIR/policies/roles.yaml}"
export AUDIT_LOG_PATH="${AUDIT_LOG_PATH:-$PROJECT_DIR/results/raw_logs.jsonl}"
export DATABASE_URL="${DATABASE_URL:-postgresql://mcp_readonly:readonly-change-me@localhost:5432/mcp_experiment}"

exec "$PROJECT_DIR/.venv/bin/python" -m mcp_server.server
