from __future__ import annotations

from mcp_server.audit import AuditLogger
from mcp_server.db import PostgresDatabase
from mcp_server.policy_engine import PolicyEngine
from mcp_server.sql_validator import SQLValidator


class SecureDatabaseTools:
    def __init__(self, db: PostgresDatabase, policy_engine: PolicyEngine, validator: SQLValidator, audit: AuditLogger):
        self.db = db
        self.policy_engine = policy_engine
        self.validator = validator
        self.audit = audit

    def listar_tabelas_permitidas(self, role: str = "analista") -> dict:
        return {"role": role, "objetos_permitidos": sorted(self.policy_engine.allowed_objects(role))}

    def descrever_esquema_autorizado(self, role: str = "analista") -> dict:
        objects = sorted(self.policy_engine.allowed_objects(role))
        return self.db.describe_views(objects)

    def executar_consulta_segura(self, role: str, sql: str) -> dict:
        allowed_objects = self.policy_engine.allowed_objects(role)
        forbidden_objects = self.policy_engine.forbidden_objects(role)
        validation = self.validator.validate(sql, allowed_objects=allowed_objects, forbidden_objects=forbidden_objects)
        if not validation.allowed:
            self.audit.log_decision(role=role, tool="executar_consulta_segura", allowed=False, reason=validation.reason, sql=sql, tables=sorted(validation.tables))
            return {"allowed": False, "reason": validation.reason, "rows": []}
        decision = self.policy_engine.authorize(role, "executar_consulta_segura", validation.tables)
        if not decision.allowed:
            self.audit.log_decision(role=role, tool="executar_consulta_segura", allowed=False, reason=decision.reason, sql=sql, tables=sorted(validation.tables))
            return {"allowed": False, "reason": decision.reason, "rows": []}
        rows = self.db.execute_query(validation.normalized_sql)
        self.audit.log_decision(role=role, tool="executar_consulta_segura", allowed=True, reason="Consulta executada", sql=validation.normalized_sql, tables=sorted(validation.tables), row_count=len(rows))
        return {"allowed": True, "reason": "Consulta executada", "sql": validation.normalized_sql, "rows": rows}
