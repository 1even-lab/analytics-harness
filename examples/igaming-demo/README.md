# Example: the harness filled in for an iGaming warehouse

The `company-data` template from this repository, filled in for one concrete warehouse: a
fictional casino operator in ClickHouse. Brands, players and numbers are invented; the shape
of the tables and their pitfalls follow a real casino mart.

Use it to see what the template looks like with every placeholder replaced, before filling it
in for your own warehouse. The demo warehouse itself is not published - the plugin is the
point, and it works against any ClickHouse that has tables of the shape below.

## What is inside

```
plugin/                    the template, filled in - install it like any plugin
  .claude-plugin/plugin.json
  .mcp.json                ClickHouse connector (mcp-clickhouse), host and password from the environment
  hooks/                   sql_guard: refuses writes, several statements, SELECT * without LIMIT
  skills/
    data-router/           what is connected → where rules and data come from
    metrics-catalog/       references/metrics.yaml - 12 metrics with the table filters
    warehouse-mart/        hand-written SQL on the `demo` database
    gaming-activity-analysis/  the casino table: the exclusion, provider pitfalls, example queries
    basic-analytics/       how to present an answer
    dashboard/             one-off HTML dashboards
  evals/                   behavioural cases for the traps + a golden set
with-platform/             the same metrics and rules for an agent platform's metric layer
```

## The data and its traps

`demo.gaming_activity` - one row per player per day per game, casino only: brand, project
code, player, geo, game, provider, aggregator, game type, and money in USD (handle,
payouts, GGR).
`demo.daily` - one row per brand per day across products; its casino GGR is already adjusted.

Three traps the plugin has to handle, and a chat without it does not:

1. One project must be excluded from the casino table entirely.
2. The provider field is not 1:1 with the game (aliases, an aggregator's name).
3. One brand has days with no rows at all.

## Running it

1. **Environment** of the person running Claude (a shell profile or a secret manager, never
   a file in git): `CLICKHOUSE_HOST`, `CLICKHOUSE_PASSWORD`. Defaults: `CLICKHOUSE_USER=demo_analyst`,
   port 8443, TLS on. The user needs `SELECT` on the warehouse and nothing else. Requires
   `uv` (`uvx`) and Claude Code.
2. **Run** with the plugin loaded:
   ```bash
   claude --plugin-dir plugin
   ```
   To install it for a team, add the plugin to a marketplace the way the root README describes.

## Evals

`plugin/evals/` - behavioural cases for the traps above (`claude plugin eval plugin`, no data
needed) and a golden set with reference values measured on the demo warehouse.
