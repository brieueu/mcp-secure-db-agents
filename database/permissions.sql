DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'mcp_readonly') THEN
        CREATE ROLE mcp_readonly LOGIN PASSWORD 'readonly-change-me';
    END IF;
END
$$;

REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO mcp_readonly;

REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM mcp_readonly;
GRANT SELECT ON filmes_publicos TO mcp_readonly;
GRANT SELECT ON filmes_mais_alugados TO mcp_readonly;
GRANT SELECT ON clientes_por_cidade TO mcp_readonly;
GRANT SELECT ON vendas_por_categoria TO mcp_readonly;
GRANT SELECT ON vendas_por_mes TO mcp_readonly;
GRANT SELECT ON receita_por_loja TO mcp_readonly;

ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM mcp_readonly;
