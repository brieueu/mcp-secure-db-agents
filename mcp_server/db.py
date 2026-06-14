from __future__ import annotations

import os
from typing import Iterable

import psycopg
from psycopg.rows import dict_row


class PostgresDatabase:
    def __init__(self, dsn: str | None = None):
        self.dsn = dsn or os.getenv("DATABASE_URL", "postgresql://mcp_readonly:readonly-change-me@localhost:5432/mcp_experiment")

    def execute_query(self, sql: str) -> list[dict]:
        with psycopg.connect(self.dsn, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                return [dict(row) for row in cur.fetchall()]

    def describe_views(self, objects: Iterable[str]) -> dict[str, list[dict]]:
        names = list(objects)
        if not names:
            return {}
        query = """
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = ANY(%s)
        ORDER BY table_name, ordinal_position
        """
        with psycopg.connect(self.dsn, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (names,))
                rows = [dict(row) for row in cur.fetchall()]
        schema: dict[str, list[dict]] = {name: [] for name in names}
        for row in rows:
            schema[row.pop("table_name")].append(row)
        return schema
