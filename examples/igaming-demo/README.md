# Example: the harness filled in for an iGaming warehouse

The `company-data` template from this repository, filled in for one concrete warehouse that
anyone can load: a fictional casino operator in ClickHouse. Brands, players and numbers are
generated; the shape of the tables and their pitfalls follow a real casino mart.

Use it to see the template working end to end before filling it in for your own warehouse.

## What is inside

```
sql/                       the warehouse: schema, deterministic data, a read-only role
plugin/                    the template, filled in - install it like any plugin
  .claude-plugin/plugin.json
  .mcp.json                ClickHouse connector (mcp-clickhouse), host and password from the environment
  hooks/                   sql_guard: refuses writes, several statements, SELECT * without LIMIT
  skills/
    data-router/           what is connected → where rules and data come from
    metrics-catalog/       references/metrics.yaml - 12 metrics with the table filters
    warehouse-mart/        hand-written SQL on the `demo` database
    gaming-activity-analysis/  the casino table: mandatory adjustments, example queries
    basic-analytics/       how to present an answer
    dashboard/             one-off HTML dashboards
  evals/                   behavioural cases for the demo's traps + a golden set
with-platform/             the same metrics and rules for an agent platform's metric layer
```

## The data and its traps

`demo.gaming_activity` - one row per player per day per game, casino only.
`demo.daily` - one row per brand per day across products; its casino GGR is already adjusted.
The window is fixed, 2026-07-04 .. 2026-10-31, so every load gives the same numbers.

Four traps are built in. The plugin handles them; a chat without it does not.

1. One project reports only real-money columns: its standard GGR, handle and payouts are NULL.
2. One project must be excluded from the casino table entirely.
3. The provider field is not 1:1 with the game (aliases, an aggregator's name).
4. One brand has no rows at all on 2026-10-20 .. 2026-10-22.

## Setup

1. **Warehouse** (an admin of a ClickHouse you can spare - never production):
   ```bash
   clickhouse-client --multiquery < sql/01_schema.sql
   ```
   ```bash
   clickhouse-client --multiquery < sql/02_data.sql
   ```
   ```bash
   clickhouse-client --multiquery < sql/03_access.sql
   ```
   Then create the `demo_analyst` user by hand - the commands are at the end of `03_access.sql`.

2. **Environment** of the person running Claude (a shell profile or a secret manager, never
   a file in git): `CLICKHOUSE_HOST`, `CLICKHOUSE_PASSWORD`. Defaults: `CLICKHOUSE_USER=demo_analyst`,
   port 8443, TLS on. Requires `uv` (`uvx`) and Claude Code.

3. **Run** with the plugin loaded:
   ```bash
   claude --plugin-dir plugin
   ```
   First check: "how many rows are in demo.gaming_activity?". To install it for a team, add
   the plugin to a marketplace the way the root README describes.

## Evals

`plugin/evals/` - cases for the traps above (`claude plugin eval plugin`) and a golden set
whose reference values are the same for every load of this dataset.
