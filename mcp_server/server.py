from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from mcp_server.audit import AuditLogger
from mcp_server.db import PostgresDatabase
from mcp_server.policy_engine import PolicyEngine
from mcp_server.sql_validator import SQLValidator
from mcp_server.tools import SecureDatabaseTools

mcp = FastMCP("mcp-secure-db-agents")
_tools = SecureDatabaseTools(
    db=PostgresDatabase(),
    policy_engine=PolicyEngine.from_yaml(os.getenv("POLICY_PATH", "policies/roles.yaml")),
    validator=SQLValidator(),
    audit=AuditLogger(os.getenv("AUDIT_LOG_PATH", "results/raw_logs.jsonl")),
)


@mcp.tool()
def listar_tabelas_permitidas(role: str = "analista") -> dict:
    """Lista apenas views autorizadas para o papel informado."""
    return _tools.listar_tabelas_permitidas(role)


@mcp.tool()
def descrever_esquema_autorizado(role: str = "analista") -> dict:
    """Descreve colunas de objetos autorizados, sem revelar tabelas sensíveis."""
    return _tools.descrever_esquema_autorizado(role)


@mcp.tool()
def executar_consulta_segura(sql: str, role: str = "analista") -> dict:
    """Valida, autoriza, audita e executa um SELECT seguro."""
    return _tools.executar_consulta_segura(role, sql)


if __name__ == "__main__":
    mcp.run()
