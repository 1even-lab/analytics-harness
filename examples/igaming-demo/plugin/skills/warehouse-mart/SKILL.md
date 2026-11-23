---
name: warehouse-mart
description: Rules for reading the demo warehouse (the `demo` database in ClickHouse) through the clickhouse MCP connector. ALWAYS use when writing SQL against the warehouse by hand - ad-hoc slices, metrics outside the catalog, finding tables and fields, reconciliations - or when the user mentions the DWH, marts, ClickHouse, the demo database. Explains how to find tables via COMMENT, why reported numbers come only from the mart layer, and how to write safe read-only queries. For catalog metrics, use metrics-catalog first.
---

# The mart layer (`demo`)

In this demo the mart layer is the `demo` database. The meaning of tables and fields is
stored in `COMMENT`s right in the warehouse metadata; metric definitions live in the catalog
(`metrics-catalog`). Standard messages to the user - [references/messages.md](references/messages.md).

## Hard rules

1. **Reported numbers come only from `demo.*`.** Data there is normalized (USD) and fields are
   documented. Access is decided by DB grants (`demo_reader` has `SELECT` on `demo.*` only):
   `ACCESS_DENIED` is not a reason to look for a workaround.
2. **Read only, `SELECT` only.** No `INSERT` / `UPDATE` / `DELETE` / `ALTER` / `DROP` /
   `TRUNCATE` / `CREATE`. The database role refuses them and the plugin's `sql_guard` hook
   refuses them before they are sent. Asked to change data - explain that access is read-only
   and point to the data engineers.
3. **Meaning comes from `COMMENT`, not from the name.** Empty `COMMENT` - warn and confirm the
   meaning with a sample or a question.
4. **The metric is in the catalog - compute it per `metrics-catalog`**, not with your own formula.
   Not in the catalog - say so directly, suggest the closest ones, agree on the formula with the user.
5. **`LIMIT`** in exploratory queries (100, for checks 10). Final aggregates with `GROUP BY` -
   no limit if the user wants the full slice. `SELECT *` without `LIMIT` is refused by the hook.
6. **Date filter by default** - the last 30 days that have data (the demo data ends on
   2026-10-31); state the window in the answer.
7. **One query - one result shape.** Don't `UNION` branches whose columns differ in type or
   meaning - two clear queries beat one clever one.
8. **SQL error - don't retry the same query.** Read the error, simplify, then retry.
   Never show the result of a failed query.
9. **Freshness and gaps.** Before answering for a window, compare the table's `max(date)` with
   the end of the window. Days with no rows inside the window are missing data, not zeros:
   name them, never fill in a zero silently.
10. **Two methods gave different numbers - that's an incident, not a choice.** Show both SQL
    queries and the discrepancy; don't pick the "more plausible" one. Casino GGR from
    `demo.gaming_activity` must match `demo.daily.casino_ggr_usd` for the same brands and dates.

## Workflow

1. **Find the table** by name **and** comment: `list_tables(database='demo')` returns tables
   with column comments. Several fit - show the candidates and let the user choose.
2. **Check the table's domain skill** - `gaming-activity-analysis` for `demo.gaming_activity`:
   it holds mandatory adjustments.
3. **Write the query:** only `demo.*`, no `SELECT *`, date filter in `WHERE` before joins,
   `GROUP BY` on specific fields, complex logic via CTEs, division as `a / nullIf(b, 0)`.
   Money columns are `Decimal(18, 2)`, and in ClickHouse `Decimal / Decimal` keeps two
   decimals (a hold of 0.0345 comes out as 0.03): divide `toFloat64(a) / nullIf(toFloat64(b), 0)`.
   Top-N: result grain = question grain ("top games" = one row per game); a field that isn't
   1:1 with the key (provider aliases) is a reference column, not a `GROUP BY` key.
4. **Show the result:** which table you used and why (per its `COMMENT`), period and filters,
   window freshness, column meanings in the words of the `COMMENT`, assumptions.

## Checklist before answering
- [ ] Numbers from `demo.*`.
- [ ] `SELECT` only; field meanings checked against `COMMENT`.
- [ ] A catalog metric is computed per spec, not from memory.
- [ ] Domain skill adjustments applied.
- [ ] Date filter present, window covered by data, gaps named.
- [ ] `LIMIT` present or it's a meaningful aggregate; no heterogeneous `UNION`.
