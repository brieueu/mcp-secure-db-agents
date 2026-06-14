from mcp_server.sql_validator import SQLValidator


def test_validator_accepts_allowed_select_and_adds_limit():
    validator = SQLValidator(allowed_objects={"vendas_por_categoria"})
    result = validator.validate("SELECT categoria, receita_total FROM vendas_por_categoria")
    assert result.allowed is True
    assert result.tables == {"vendas_por_categoria"}
    assert "LIMIT 100" in result.normalized_sql.upper()


def test_validator_blocks_destructive_sql():
    validator = SQLValidator(allowed_objects={"vendas_por_categoria"})
    result = validator.validate("DROP TABLE customer")
    assert result.allowed is False
    assert "select" in result.reason.lower() or "destrut" in result.reason.lower()


def test_validator_blocks_forbidden_sensitive_table():
    validator = SQLValidator(allowed_objects={"vendas_por_categoria"}, forbidden_objects={"payment", "customer"})
    result = validator.validate("SELECT * FROM payment LIMIT 5")
    assert result.allowed is False
    assert "payment" in result.reason


def test_validator_blocks_catalog_schema():
    validator = SQLValidator(allowed_objects={"vendas_por_categoria"})
    result = validator.validate("SELECT * FROM pg_catalog.pg_tables")
    assert result.allowed is False
    assert "schema" in result.reason.lower() or "catálogo" in result.reason.lower()
