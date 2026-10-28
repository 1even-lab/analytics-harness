---
name: warehouse-mart
description: Rules for reading the analytical warehouse (the mart layer) through an MCP connector. ALWAYS use when writing SQL against the warehouse by hand - ad-hoc slices, metrics outside the catalog, finding tables and fields, reconciliations - or when the user mentions the DWH, marts, data marts, <warehouse>. Explains how to find tables via COMMENT, why reported numbers come only from mart, and how to write safe read-only queries. For catalog metrics, use metrics-catalog first.
---

# The `mart` layer

The meaning of tables and fields is stored in `COMMENT`s right in the warehouse metadata;
metric definitions live in the catalog (`metrics-catalog`). Standard messages to the user -
[references/messages.md](references/messages.md).

## Hard rules

1. **Reported numbers come only from `mart`.** Data there is normalized (currency, test and
   deleted records removed) and fields are documented. `raw`, `core`, `staging`, `sandbox` are
   not used for reported numbers. You may go there to investigate (checking a load, a
   discrepancy, a field missing from the mart) - but say it's a raw layer and don't present the
   result as a reported number. Access is decided by DB grants: `ACCESS_DENIED` is not a reason
   to look for a workaround.
2. **Dictionaries** `dict.*` - for joins and lookups; no fact numbers come from there.
3. **Read only, `SELECT` only.** No `INSERT` / `UPDATE` / `DELETE` / `ALTER` / `DROP` /
   `TRUNCATE` / `CREATE`, even if the connector allows it. Asked to change data - explain that
   access is read-only and point to the data engineers.
4. **Meaning comes from `COMMENT`, not from the name.** `bet_amount` may turn out to be in cents.
   Empty `COMMENT` - warn and confirm the meaning with a sample or a question.
5. **The metric is in the catalog - compute it per `metrics-catalog`**, not with your own formula.
   Not in the catalog - say so directly, suggest the closest ones, agree on the formula with the user.
6. **`LIMIT`** in exploratory queries (100, for checks 10). Final aggregates with `GROUP BY` -
   no limit if the user wants the full slice.
7. **Date filter by default** - the last 30 full days; state the window in the answer.
8. **One query - one result shape.** Don't `UNION` branches whose columns differ in type or
   meaning - two clear queries beat one clever one.
9. **SQL error - don't retry the same query.** Read the error, simplify, then retry.
   Never show the result of a failed query.
10. **Freshness.** Before answering for "the last N days", compare the table's `max(<date>)`
    with the end of the window. Yesterday's load didn't arrive - say so explicitly; don't pass
    off a short window as a full one.
11. **Two methods gave different numbers - that's an incident, not a choice.** Show both SQL
    queries and the discrepancy; don't pick the "more plausible" one.

## Workflow

1. **Find the table** by name **and** comment; several fit - show the candidates and let the
   user choose. Replace `information_schema` with your dialect's catalog:
   ```sql
   SELECT table_name, column_name, data_type, column_comment
   FROM information_schema.columns
   WHERE table_schema = 'mart'
     AND (lower(column_name) LIKE '%ggr%' OR lower(column_comment) LIKE '%ggr%')
   ```
2. **Check the table's domain skill** (`<domain>-analysis`): it holds mandatory adjustments.
3. **Write the query:** only `mart.*` (+ `dict.*`), no `SELECT *`, date filter in `WHERE`
   before joins, `GROUP BY` on specific fields, complex logic via CTEs, division as
   `a / nullif(b, 0)`. Top-N: result grain = question grain ("top games" = one row per game);
   a field that isn't 1:1 with the key (provider aliases) is a reference column, not a
   `GROUP BY` key.
4. **Show the result:** which table you used and why (per its `COMMENT`), period and filters,
   window freshness, column meanings in the words of the `COMMENT`, assumptions.

## Checklist before answering
- [ ] Numbers from `mart.*`; a raw layer, if used, is called out.
- [ ] `SELECT` only; field meanings checked against `COMMENT`.
- [ ] A catalog metric is computed per spec, not from memory.
- [ ] Domain skill adjustments applied.
- [ ] Date filter present, window covered by data.
- [ ] `LIMIT` present or it's a meaningful aggregate; no heterogeneous `UNION`.
