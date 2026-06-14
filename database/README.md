# Database

Esta pasta conterá os scripts de inicialização do PostgreSQL usados no experimento.

Ordem planejada dos scripts:

1. `01_schema.sql` — schema da base pública escolhida, preferencialmente Sakila PostgreSQL.
2. `02_data.sql` — carga inicial dos dados.
3. `03_views.sql` — views seguras expostas ao agente LLM.
4. `04_permissions.sql` — usuários, papéis e permissões de acesso somente leitura.

Os scripts em `database/init/` são montados automaticamente pelo `docker-compose.yml` em `/docker-entrypoint-initdb.d`.
