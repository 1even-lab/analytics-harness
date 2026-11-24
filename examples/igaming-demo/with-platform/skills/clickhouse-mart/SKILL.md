---
name: clickhouse-mart
description: How to work with the analytical mart layer of the demo project in ClickHouse through the platform. Use ALWAYS when the user asks about data, metrics, reports, analytics, KPIs, business numbers, marts, or mentions ClickHouse / CH — even without saying "look in the mart". Covers finding tables and fields through COMMENT metadata (clickhouse_schema), taking metric definitions and formulas from the platform metric catalog (list_metrics / query_metric), writing safe SELECT queries over the mart layer, and why reporting numbers come from marts.
---

# ClickHouse Mart Layer

For analysts and business users who get numbers and build reports on the mart layer of
the `demo` project in ClickHouse (the database `demo`; data is fictional, made for a
workshop). The meaning of tables and fields lives in `COMMENT`s in the metadata; metric
definitions and formulas live in the **platform metric catalog** (`list_metrics` /
`query_metric`; its source is `semantics/metrics_demo.yaml` in git). This skill explains
how to use them instead of guessing column meanings and formulas.

Domain skill on top of this one: `gaming-analysis` — the casino vertical
(`demo.gaming_activity`).

## When to apply

As soon as any of these appears in the request:

- ClickHouse / CH mentioned directly.
- A request to compute a metric, build a report, pull a sample, compare periods, find a top, look at a trend.
- "How many…", "what is…", "show…", "compute…", "how did … change", "by …" about business data.
- Marts, data marts, DWH, reporting, BI, metrics, KPIs.

When in doubt, apply it.

## Hard rules

1. **Analytics is built on the mart layer (`demo`).** Reporting numbers come from
   `demo.*`: data there is normalized (USD), fields are described in `COMMENT`. Access to
   layers is decided by the database grants: the platform runs the query under the role
   of the caller. No grant — ClickHouse refuses with `ACCESS_DENIED`, and that is a reason
   to tell the user who grants access, not to look for a workaround.
2. **Structure and `COMMENT`s come from `clickhouse_schema`** (step 2). Direct queries to
   `system.*` / `information_schema.*` are refused by the platform gateway.
3. **Read-only, `SELECT` only.** The gateway lets through one `SELECT` per call;
   `INSERT` / `UPDATE` / `ALTER` / `DROP` / `TRUNCATE` / `CREATE` and other mutations, as
   well as `SHOW` / `DESCRIBE`, are refused. If asked to change something, explain that
   the path is read-only and point to the data engineers.
4. **Meaning comes from metadata, not from names.**
   - **Fields and tables** — check `COMMENT`. Names mislead.
   - **Metrics and formulas** — from the platform catalog, not from memory. Before
     explaining or computing a metric (GGR, hold, ARPPU…) find it with `list_metrics` and
     compute it with `query_metric`: the formula and the mandatory adjustments are already
     built into the layer.
5. **Always `LIMIT`** exploratory queries (100 as a rule, 10 for checks). Final aggregates
   with `GROUP BY` may go without a limit when the user wants the whole cut.
6. **Date filter by default.** If the table has a date column and the user gave no
   period, take **the last 30 days** (`date >= today() - 30 AND date < today()`) and say
   which window you took.
7. **One query, one result shape.** Do not glue result sets with different column types
   or meanings through `UNION` (ClickHouse rejects it with `NO_COMMON_TYPE`). Two clear
   queries beat one clever `UNION`.
8. **SQL error — do not repeat the same query.** Read the exception, simplify, then
   retry. Never show a result built on a query that failed.
9. **A mismatch between the layer and manual SQL is an incident, not a choice.** If
   `query_metric` and your manual query give different numbers for the same question, stop
   and show BOTH queries. Do not pick the "more plausible" number: something lost a rule,
   and that gets fixed, not hidden.
10. **Freshness for "last N days" in manual SQL.** `query_metric` returns `data_through` /
    `window_covered` itself; in manual SQL check `max(date)` of the table against the end
    of the window before presenting. Missing days inside the window are missing data, not
    zeros: name them.

## Workflow

### Step 1. Check the platform and the project

Data goes through the agent platform's MCP server (its gateway): permissions
are checked on every call, credentials stay on the server. If it is not connected, say so:
without it there are no rules and no data.

Every data call needs `project_key`. Here it is **`demo`**; say so in the answer.

### Step 2. Find the mart with `clickhouse_schema`

```
clickhouse_schema(project_key="demo")
```

The answer is a snapshot of tables with columns and `COMMENT`s. **This is the main source
of truth about meaning**: the table comment describes the mart, the column comment
describes the field. Match the question against both name and comment.

If a table has an empty comment and unclear columns, warn about it and confirm the
meaning with a small `SELECT` sample or a clarifying question.

### Step 3. Take the metric from the catalog

If the question is about a specific metric, find it first: `list_metrics(project_key="demo")`
returns for each metric its `title`, descriptions, allowed `dims` and source table. Compute
it with `query_metric`: formula, grain and mandatory adjustments are built into the layer,
the same question always compiles to the same SQL (it comes back with the answer, the
mandatory filters as a separate `mandatory_where` field).

If the metric is not in the catalog, say so, offer the closest ones from `list_metrics`
and, if it is needed regularly, suggest adding a spec through an MR to
`semantics/metrics_demo.yaml`. Do not invent a formula.

### Step 4. Write and run a manual query (only when the catalog does not cover it)

- Data tables in `FROM` / `JOIN` only from `demo.*`.
- **No `SELECT *`** — list the fields.
- Filter by date as early as possible (in `WHERE`, before joins and aggregation).
- `GROUP BY` concrete dimensions, not `GROUP BY ALL`.
- Tops — `ORDER BY … LIMIT N`. Windows — `OVER (…)`. Cohorts and complex cuts — CTE.

```sql
SELECT
    date,
    company,
    round(sum(deposits_usd), 2) AS deposits_usd,
    sum(registrations)          AS registrations
FROM demo.daily
WHERE date >= today() - 30
  AND date <  today()
GROUP BY date, company
ORDER BY date DESC, deposits_usd DESC
LIMIT 10 BY date
```

Run it with `clickhouse_query(project_key="demo", sql="...")` (up to 500 rows per call;
for a bigger cut narrow the query or aggregate).

### Step 5. Present and explain

1. Which project and table you took and why (with its `comment`).
2. Period and filters; freshness of the window (rule 10).
3. What the columns mean — in the words of `comment`; metric definitions from the catalog.
4. Assumptions you made.

## Ambiguous cases

- **Several tables fit.** List the candidates (name + `comment`) and let the user pick.
- **A field that does not exist.** Look for synonyms in comments; not found — say so.
- **Asked to change or delete data.** Refuse: read-only.

## Period comparison (WoW / MoM)

For catalog metrics a period comparison is **two `query_metric` calls** with different
windows (current and previous of the same length), not arithmetic over daily rows: the
layer applies the formula and adjustments to each window as a whole. `uniq` metrics are
not additive and ratio metrics cannot be rebuilt by dividing your own sums.

A manual `sumIf` pattern is fine only for fields outside the catalog:

```sql
SELECT
    sumIf(x, date >= today() - 7)                            AS last_7d,
    sumIf(x, date >= today() - 14 AND date < today() - 7)    AS prev_7d,
    round((last_7d - prev_7d) / nullIf(prev_7d, 0) * 100, 2) AS delta_pct
FROM demo.<table>
WHERE date >= today() - 14 AND date < today()
```

## Useful ClickHouse functions

- Dates: `today()`, `toStartOfWeek/Month()`, `toMonday()`, `dateDiff('day', a, b)`.
- Safe division: `a / nullIf(b, 0)`. Money columns are `Decimal(18, 2)`, and `Decimal / Decimal`
  keeps two decimals (a hold of 0.0345 comes out as 0.03): divide
  `toFloat64(a) / nullIf(toFloat64(b), 0)`.
- Conditional aggregates: `sumIf`, `countIf`, `uniqIf`.
- Distinct: `uniq()` (fast, approximate), `uniqExact()` (exact).

## Checklist before answering

- [ ] Project `demo` named in the answer?
- [ ] Numbers from `demo.*`?
- [ ] One `SELECT` per call; structure from `clickhouse_schema`?
- [ ] Field meaning checked against `COMMENT`?
- [ ] Metric taken from the catalog (`list_metrics` / `query_metric`), not from memory?
- [ ] `LIMIT` in place (or a meaningful aggregate)?
- [ ] Date filter present; window covered by data, missing days named?
- [ ] Said which mart and why?
