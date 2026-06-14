# MCP Secure DB Agents

Implementação e avaliação de uma arquitetura baseada em **Model Context Protocol (MCP)** para mediar consultas de agentes LLM a bancos relacionais. O MVP usa PostgreSQL/Sakila, views seguras, políticas YAML, validação SQL, auditoria JSONL, ferramentas MCP e um runner local compatível com Qwen2.5-Coder.

## Objetivo

Comparar a mediação por MCP com acesso direto ao banco, medindo segurança, controle, rastreabilidade e utilidade das respostas.

## Arquitetura resumida

```text
Usuário → agente Python → Qwen local → ferramentas MCP → validação/política/auditoria → PostgreSQL read-only
```

O agente não acessa o banco diretamente. Toda consulta passa por `listar_tabelas_permitidas`, `descrever_esquema_autorizado` e `executar_consulta_segura`.

## Estrutura

```text
agent/          cliente local do modelo, prompts e runner
mcp_server/     servidor MCP, ferramentas, validação, políticas, DB e auditoria
policies/       políticas de acesso por papel
database/       views seguras e permissões PostgreSQL
data/           Sakila PostgreSQL e seed de indirect prompt injection
experiments/    prompts, execução, baseline e análise
results/        logs e métricas gerados localmente
docs/           documentação metodológica e reprodutibilidade
paper/          artigo local ignorado pelo Git
```

## Setup Python

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -U pip
.venv/bin/python -m pip install -e '.[dev,analysis]'
```

## Banco PostgreSQL/Sakila

```bash
docker compose config
docker compose down -v
docker compose up -d
docker compose exec postgres psql -U mcp_user -d mcp_experiment -c "\dv"
docker compose exec postgres psql -U mcp_readonly -d mcp_experiment -c "SELECT * FROM vendas_por_categoria LIMIT 5;"
docker compose exec postgres psql -U mcp_readonly -d mcp_experiment -c "SELECT * FROM payment LIMIT 5;"  # deve falhar
```

## Qwen2.5-Coder local

O código aceita qualquer backend local compatível com a API OpenAI:

```text
LOCAL_LLM_BASE_URL=http://localhost:11434/v1
LOCAL_LLM_MODEL=qwen2.5-coder:7b
LOCAL_LLM_API_KEY=local-not-needed
```

Pode ser Ollama, LM Studio, llama.cpp ou vLLM, desde que exponha `/v1/chat/completions`.

## Testes

```bash
.venv/bin/python -m pytest -q
```

## Experimentos

```bash
.venv/bin/python -m experiments.run_experiment --limit 5
.venv/bin/python -m experiments.analyze_results --input results/raw_logs.jsonl
```

## Critérios de avaliação

- bloqueio de SQL destrutivo, tabelas sensíveis e schemas de catálogo;
- uso de views agregadas/anonimizadas e usuário PostgreSQL read-only;
- rastreabilidade por auditoria JSONL;
- resistência a indirect prompt injection;
- comparação com baseline direto em taxa de sucesso, recusas corretas e utilidade das respostas.
