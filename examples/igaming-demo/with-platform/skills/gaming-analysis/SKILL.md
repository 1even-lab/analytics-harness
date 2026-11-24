---
name: gaming-analysis
description: Rules and reference for the demo.gaming_activity casino mart in ClickHouse — its fields, the mandatory adjustment and ready query examples. Use when you write SQL over gaming_activity BY HAND — fields, providers and games, reconciliation with demo.daily. For catalog metrics (list_metrics → query_metric) this skill is not needed: the layer compiles the mandatory project exclusion into the SQL itself and returns it in mandatory_where. The adjustment and its reason are in the body of the skill, not in this description. Applies on top of clickhouse-mart and does not lift its rules (mart only, read-only, field meaning from COMMENT).
---

# Gaming Analysis — `demo.gaming_activity`

An add-on to `clickhouse-mart`. Its hard rules still apply (`demo` only, `SELECT` only,
date filter by default, field meaning from `COMMENT`).

## Mart and grain

`demo.gaming_activity` is **one row per player per day per game / provider / aggregator**.
Casino vertical only (slots and other casino games): no sportsbook, poker or payments.
Cross-product numbers and daily profitability come from `demo.daily`.

Money is in **USD**, `Decimal(18, 2)`; ratios divide `toFloat64` (see `clickhouse-mart`).

`game_name` and `game_type` are normalized. **`game_provider` is not fully
normalized and is NOT 1:1 with the game**: one game shows up under provider aliases
(`Skyline Studio` / `Skyline` / `Undefined`), and aggregator names leak into the
provider field (`HubX`, while its own `game_aggregator` is often `Undefined`). Until
provider normalization is done: **do not put the provider into GROUP BY of game tops**
(example 5), and treat provider cuts (example 3) as an approximation.

## Mandatory adjustment (always)

### Project 190 — exclude entirely

Project `190` is excluded from `gaming_activity` **entirely and always** — in every
sample, aggregate and metric over this mart, not only when reconciling with daily:

```sql
WHERE project != '190'
```

`project` is a string code: compare with strings (`'190'`), not numbers.

## Fields

Dimensions: `company` (brand), `project` (code), `user_id`, `geo`, `platform`
(web / mobile), `traffic_source_grouped` (organic / paid), `is_vip`, `reg_date`, `date`
(activity date), `game_name`, `game_provider`, `game_aggregator`, `game_type`.

Money and counts:

- **Bet / handle** — `casino_bet_amount_usd`
- **Win / payouts** — `casino_win_amount_usd`
- **GGR** — `casino_ggr_usd`
- **Bet count** — `casino_bet_count`

## Metric definitions — from the platform catalog

Formulas come from the catalog (`list_metrics` / `query_metric`) under the rule of
`clickhouse-mart`, not from memory. Casino metrics of this mart carry the `_games` suffix
(`ggr_games`, `rtp_games`, …); prefer `query_metric` for them — the exclusion is already
built into the layer. This skill defines the mart specifics for manual SQL.
The building block for every manual GGR:

```sql
sum(casino_ggr_usd)   -- always with WHERE project != '190'
```

## Examples

### 1. GGR by day and brand — canonical reconciliation with daily

```sql
SELECT
    date,
    company,
    round(sum(casino_ggr_usd), 2) AS ggr_usd
FROM demo.gaming_activity
WHERE date >= today() - 30
  AND date <  today()
  AND project != '190'
GROUP BY date, company
ORDER BY date DESC, ggr_usd DESC
LIMIT 1000
```

### 2. GGR / hold / players by brand for a period

```sql
SELECT
    company,
    round(sum(casino_ggr_usd), 2)               AS ggr_usd,
    round(sum(casino_bet_amount_usd), 2) AS bet_usd,
    round(toFloat64(ggr_usd) / nullIf(toFloat64(bet_usd), 0) * 100, 2)                                          AS hold_pct,
    uniqExact(user_id)                                                                    AS active_players
FROM demo.gaming_activity
WHERE date >= today() - 30
  AND date <  today()
  AND project != '190'
GROUP BY company
ORDER BY ggr_usd DESC
```

### 3. Top providers by GGR

⚠️ Provider numbers are an approximation: aliases and aggregators in
`game_provider` spread part of a real provider's GGR over other values. Say so
in the answer.

```sql
SELECT
    game_provider,
    round(sum(casino_ggr_usd), 2) AS ggr_usd,
    uniqExact(user_id)                                                      AS players
FROM demo.gaming_activity
WHERE date >= today() - 30
  AND date <  today()
  AND project != '190'
GROUP BY game_provider
ORDER BY ggr_usd DESC
LIMIT 20
```

### 4. Week over week GGR

For the catalog metric use two `query_metric` calls (see `clickhouse-mart`). Manual form:

```sql
SELECT
    sumIf(casino_ggr_usd, date >= today() - 7)                         AS last_7d,
    sumIf(casino_ggr_usd, date >= today() - 14 AND date < today() - 7) AS prev_7d,
    round(toFloat64(last_7d - prev_7d) / nullIf(toFloat64(prev_7d), 0) * 100, 2)                                                    AS delta_pct
FROM demo.gaming_activity
WHERE date >= today() - 14
  AND date <  today()
  AND project != '190'
```

### 5. Top games for a period

The result grain must match the question: "top games" = one row per `game_name`.
**Do not put `game_provider` into GROUP BY**: the field is not 1:1 with the
game, and the top silently turns into a top of game slices — GGR of one game spreads
below the LIMIT, aliases get lost. Give the provider as a reference column:

```sql
SELECT
    game_name,
    round(sum(casino_ggr_usd), 2)               AS ggr_usd,
    round(sum(casino_bet_amount_usd), 2) AS bet_usd,
    uniqExact(user_id)                                                                    AS players,
    groupUniqArray(game_provider)                                               AS providers  -- reference only
FROM demo.gaming_activity
WHERE date >= today() - 30
  AND date <  today()
  AND project != '190'
GROUP BY game_name
ORDER BY ggr_usd DESC
LIMIT 30
```

The reverse catch: the same `game_name` at different providers is sometimes really a
different game, especially live tables (`Dragon Tiger Live`, `Lucky Wheel Live`). If the
`providers` column of a game you analyse has more than one value, check whether those are
aliases of one product or different games, and say it.

## What to say in the answer

Apply the exclusion **always**, but **do not reveal internal project codes** to the user:
codes are not for every recipient. The exclusion is a detail of the query, not part of the
answer: keep it in SQL.

When answering over `gaming_activity`, state:

1. That the mandatory methodology adjustment was applied (in general terms, no code). If you
   need to explain a difference with a naive number, say that one project is excluded,
   without naming it by code.
2. That the mart covers casino only; cross-product numbers come from `demo.daily`.
3. Period and filters, as `clickhouse-mart` requires.

Where possible compute through `query_metric` (`*_games` metrics): there the exclusion lives
in the metric layer and codes do not reach the output at all.
