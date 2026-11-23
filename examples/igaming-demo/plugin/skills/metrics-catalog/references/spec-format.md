# Metric spec format and compilation into SQL

## File structure

```yaml
version: 1
tables:                      # filters shared by ALL metrics of a table - written once
  <db>.<table>:
    where: ["is_test = 0"]
    final: false
metrics:
  <key>:                     # stable slug, snake_case; never renamed
    title: "$ GGR"           # canonical name the user sees
    description: "..."       # what it is and when to use it
    table: <db>.<table>
    time_column: date
    unit: USD                # USD | count | users | pct | ratio
    expression: "sum(bet_usd) - sum(win_usd)"
    dims:                    # alias → column; the metric has no other breakdowns
      date: date
      country: country
    where: ["status = 'settled'"]     # filters specific to this metric
    dedup: ...               # optional, see below
    caveat: "..."            # applicability limit, 1-2 sentences
    owner: "<team>"
```

| field | req. | meaning |
|---|---|---|
| `title` | yes | canonical name; unit prefix (`$`, `#`, `%`) consistent with neighbors |
| `description` | yes | everything a person needs to know before using it |
| `table`, `time_column`, `expression` | yes | table, period column, aggregate |
| `unit` | yes | number format in the answer |
| `dims` | yes | allowed breakdowns; `{}` - total only |
| `where` | no | metric filters (table-wide ones go in `tables`) |
| `final` | no | `true` - read with engine-level dedup (tables with asynchronous dedup) |
| `dedup` | no | the measure lives on a coarser grain than the table's rows |
| `caveat` | no | what the formula can't express: scope, non-additivity, dates |
| `owner` | yes | who owns the definition |

## Compiling a spec into SQL

A request "`<metric>` for `[start, end)` broken down by `<dim1>, <dim2>`" compiles to:

```sql
SELECT
    <dims[dim1]> AS <dim1>
    , <dims[dim2]> AS <dim2>
    , <expression> AS <metric>
FROM <table> [FINAL]                          -- if tables.<table>.final or metric.final
WHERE <time_column> >= '<start>'
  AND <time_column> <  '<end>'
  AND <every condition in tables.<table>.where>
  AND <every condition in metric.where>
GROUP BY <dim1>, <dim2>
```

With no breakdown - no dimensions in `SELECT` and no `GROUP BY`: that is the total. **The total
is a separate query**, not the sum of breakdown rows (for `count(DISTINCT)` and ratios these
are different numbers).

### Example

Spec `ggr_games` from `metrics.yaml`, question: "GGR by brand for August".

```sql
SELECT
    company AS brand
    , round(sum(if(project = '170', casino_ggr_real_usd, casino_ggr_usd)), 2) AS ggr_games
FROM demo.gaming_activity
WHERE date >= '2026-08-01'
  AND date <  '2026-09-01'
  AND project != '190'           -- tables.demo.gaming_activity.where
GROUP BY brand
```

## `dedup` - a measure on a coarser grain

If a table repeats one value across several rows (a campaign budget on every day it is active),
a plain `sum` multiplies it by the number of rows. Such a measure is marked:

```yaml
dedup:
  by: [campaign_id, month]      # the grain the value belongs to
  measure:
    budget_usd: once            # repeated across rows → take once per grain
    clicks: sum                 # each row has its own → add up
```

Compilation - first collapse to the `by` grain, then aggregate:

```sql
WITH grain AS (
    SELECT
        campaign_id, month
        , any(budget_usd) AS budget_usd      -- once
        , sum(clicks) AS clicks              -- sum
    FROM mart.campaign_daily
    WHERE <window and filters>
    GROUP BY campaign_id, month
)
SELECT sum(budget_usd) AS budget_usd, sum(clicks) AS clicks FROM grain
```

A breakdown **below** the `by` grain gives no correct number for such a metric (the value is
repeated, not split) - refuse and explain. Filtering by such a column is fine.

## File maintenance rules

- A metric key is stable; `title` may be renamed, the key may not.
- A filter that holds for all metrics of a table goes in `tables.<t>.where`, not into each
  metric: per-metric copies of such filters get forgotten.
- Better than a filter in the spec is a filter in the warehouse (row policy / view): it can't
  be forgotten.
- `caveat` - one or two sentences; anything longer goes into the table's domain skill.
- Before merge: `python scripts/validate_metrics.py` and a reconciliation of the number with an
  independent source (BI report, hand-written SQL) for one period.
