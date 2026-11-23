-- Read-only access for the harness. Privileges live on a ROLE; the user only gets the role.
-- Run as an admin of the demo ClickHouse:
--   clickhouse-client --multiquery < sql/03_access.sql
--
-- No `readonly` setting on the user: the MCP server sets its own per query, and a user
-- pinned to readonly=1 cannot accept that. Read-only comes from the grants: SELECT only.

CREATE ROLE IF NOT EXISTS demo_reader;
GRANT SELECT ON demo.* TO demo_reader;

-- The user is created by hand, so the password never lands in a file. With the password
-- in a shell variable (read -s DEMO_PWD):
--   clickhouse-client -q "CREATE USER IF NOT EXISTS demo_analyst
--       IDENTIFIED WITH sha256_password BY '$DEMO_PWD'"
--   clickhouse-client -q "GRANT demo_reader TO demo_analyst"
--   clickhouse-client -q "SET DEFAULT ROLE demo_reader TO demo_analyst"
-- The analyst puts the same password into CLICKHOUSE_PASSWORD in their own environment.
