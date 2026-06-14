# MCP Secure DB Agents

Arquitetura baseada em **Model Context Protocol (MCP)** para consultas seguras de agentes LLM a bancos de dados relacionais.

Este repositório reúne a documentação, implementação experimental e materiais de avaliação de uma arquitetura que posiciona o MCP como camada intermediária entre agentes LLM e bancos de dados. O foco do projeto é investigar mecanismos de validação SQL, controle de acesso, auditoria e mitigação de riscos como *prompt injection*, *indirect prompt injection* e *tool poisoning*.

## Objetivo

Avaliar se uma arquitetura mediada por MCP aumenta a segurança, o controle e a rastreabilidade de consultas realizadas por agentes LLM em bancos de dados relacionais, quando comparada a uma integração direta entre agente e banco.

## Arquitetura resumida

```text
Usuário
  → Interface Conversacional
  → Agente LLM Orquestrador
  → Cliente MCP
  → Servidor MCP
      → Gateway de Entrada
      → Autenticação / Identificação
      → Validador SQL
      → Motor de Políticas
      → Adaptador SQL
  → Banco de Dados Relacional
```

O agente LLM não possui acesso direto ao banco. Toda consulta passa por ferramentas MCP controladas, como `listar_tabelas_permitidas`, `descrever_esquema_autorizado` e `executar_consulta_segura`.

## Estrutura do repositório

```text
data/               # datasets brutos, seeds e casos adicionais
database/           # scripts SQL de schema, views e permissões
mcp_server/         # servidor MCP, ferramentas, validador, políticas e auditoria
agent/              # agente/runner experimental
policies/           # políticas de acesso em YAML
experiments/        # prompts, execução experimental e análise
results/            # resultados brutos, métricas processadas e figuras
tests/              # testes automatizados
paper/              # seções e figuras do artigo
```

## Stack planejada

- Python 3.11+
- MCP Python SDK / FastMCP
- PostgreSQL via Docker Compose
- SQLGlot para validação SQL
- psycopg para conexão com PostgreSQL
- Pydantic e PyYAML para validação/configuração
- pytest para testes
- Pandas/Matplotlib/Seaborn para análise dos resultados

## Status

Projeto em estruturação inicial. A próxima etapa é configurar o PostgreSQL local e carregar uma base pública relacional, preferencialmente Sakila PostgreSQL.
