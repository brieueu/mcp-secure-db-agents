from __future__ import annotations

from dataclasses import dataclass, field

import sqlglot
from sqlglot import exp

CATALOG_SCHEMAS = {"pg_catalog", "information_schema"}
DESTRUCTIVE_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE", "GRANT", "REVOKE", "COPY", "CALL", "DO"
}
DEFAULT_FORBIDDEN = {"payment", "customer", "address", "staff", "rental"}


@dataclass(frozen=True)
class ValidationResult:
    allowed: bool
    reason: str
    normalized_sql: str = ""
    tables: set[str] = field(default_factory=set)


class SQLValidator:
    def __init__(self, allowed_objects: set[str] | None = None, forbidden_objects: set[str] | None = None, default_limit: int = 100):
        self.allowed_objects = {o.lower() for o in allowed_objects} if allowed_objects else set()
        self.forbidden_objects = {o.lower() for o in (forbidden_objects or DEFAULT_FORBIDDEN)}
        self.default_limit = default_limit

    def validate(self, sql: str, allowed_objects: set[str] | None = None, forbidden_objects: set[str] | None = None) -> ValidationResult:
        sql = (sql or "").strip()
        if not sql:
            return ValidationResult(False, "SQL vazio")
        if self._has_multiple_statements(sql):
            return ValidationResult(False, "Múltiplas instruções SQL não são permitidas")
        first = sql.split(None, 1)[0].upper().strip("(")
        if first in DESTRUCTIVE_KEYWORDS or first != "SELECT":
            return ValidationResult(False, "Apenas consultas SELECT são permitidas")
        try:
            tree = sqlglot.parse_one(sql, read="postgres")
        except Exception as exc:  # pragma: no cover - mensagem depende do parser
            return ValidationResult(False, f"SQL inválido: {exc}")
        if not isinstance(tree, exp.Select):
            return ValidationResult(False, "Apenas SELECT simples é permitido")

        schemas = {table.db.lower() for table in tree.find_all(exp.Table) if table.db}
        forbidden_schemas = schemas & CATALOG_SCHEMAS
        if forbidden_schemas:
            return ValidationResult(False, f"Acesso a schema de catálogo bloqueado: {sorted(forbidden_schemas)}")

        tables = {table.name.lower() for table in tree.find_all(exp.Table)}
        effective_forbidden = self.forbidden_objects | {o.lower() for o in (forbidden_objects or set())}
        blocked = tables & effective_forbidden
        if blocked:
            return ValidationResult(False, f"Objeto bloqueado pela política: {', '.join(sorted(blocked))}", tables=tables)

        effective_allowed = {o.lower() for o in (allowed_objects or self.allowed_objects)}
        if effective_allowed and not tables.issubset(effective_allowed):
            denied = tables - effective_allowed
            return ValidationResult(False, f"Objeto não autorizado: {', '.join(sorted(denied))}", tables=tables)

        if tree.args.get("limit") is None:
            tree = tree.limit(self.default_limit)
        return ValidationResult(True, "Consulta aprovada", normalized_sql=tree.sql(dialect="postgres"), tables=tables)

    @staticmethod
    def _has_multiple_statements(sql: str) -> bool:
        stripped = sql.strip().rstrip(";")
        return ";" in stripped
