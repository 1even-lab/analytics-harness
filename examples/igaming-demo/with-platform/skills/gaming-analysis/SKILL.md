---
name: gaming-analysis
description: Rules and reference for the demo.gaming_activity casino mart in ClickHouse — its fields, the mandatory GGR adjustments and ready query examples. Use when you write SQL over gaming_activity BY HAND — fields, providers and games, reconciliation with demo.daily. For catalog metrics (list_metrics → query_metric) this skill is not needed: the layer compiles the mandatory project adjustments into the SQL itself and returns them in mandatory_where. The adjustments and their reasons are in the body of the skill, not in this description. Applies on top of clickhouse-mart and does not lift its rules (mart only, read-only, field meaning from COMMENT).
---

# Gaming Analysis — `demo.gaming_activity`

An add-on to `clickhouse-mart`. Its hard rules still apply (`demo` only, `SELECT` only,
date filter by default, field meaning from `COMMENT`).

## Mart and grain

`demo.gaming_activity` is **one row per player per day per game / provider / aggregator**.
Casino vertical only (slots and other casino games): no sportsbook, poker or payments.
Cross-product numbers and daily profitability come from `demo.daily`.

Money is in **USD** (`*_usd`). Money and count fields are `Nullable`: use `sum()` /
`nullIf()` and do not treat NULL as zero by hand.

`game_name` and `game_type` are normalized. **`game_provider_full_name` is not fully
normalized and is NOT 1:1 with the game**: one game shows up under provider aliases
(`Skyline Studio` / `Skyline` / `Undefined`), and aggregator names leak into the
provider field (`HubX`, while its own `game_aggregator` is often `Undefined`). Until
provider normalization is done: **do not put the provider into GROUP BY of game tops**
(example 5), and treat provider cuts (example 3) as an approximation.

## Mandatory GGR adjustments (always)

### Rule 1. Project 170 — the real-money family

Project `170` has **all standard money columns empty (NULL)**, not just GGR: only the
real-money family is filled. Summing the standard columns directly silently drops the
project, so the substitution goes into EVERY money aggregate:

```sql
if(project = '170', casino_ggr_real_usd, casino_ggr_usd)                 -- GGR
if(project = '170', casino_bet_amount_real_usd, casino_bet_amount_usd)   -- handle
if(project = '170', casino_win_amount_real_usd, casino_win_amount_usd)   -- payouts
```

Fixing GGR and reading the rest raw is worse than not fixing anything: the project is in
GGR and missing from handle, so hold and RTP in the same answer stop agreeing.

**Project `170` has no bet counter in any form**: `casino_bet_count` is NULL and
`casino_bet_count_real` is zero. So the number of bets for this project is not computed
at all, and "was active" is taken from handle: a condition like
`coalesce(casino_bet_count, 0) > 0` removes every player of the project.

All other projects use the standard columns; the real family is substituted **only** for `170`.

### Rule 2. Project 190 — exclude entirely

Project `190` is excluded from `gaming_activity` **entirely and always** — in every
sample, aggregate and metric over this mart, not only when reconciling with daily:

```sql
WHERE project != '190'
```

`project` is a string code: compare with strings (`'170'`, `'190'`), not numbers.

## Fields

Dimensions: `company` (brand), `project` (code), `user_id`, `geo`, `platform`
(web / mobile), `traffic_source_grouped` (organic / paid), `is_vip`, `reg_date`, `date`
(activity date), `game_name`, `game_provider_full_name`, `game_aggregator`, `game_type`.

Money and counts (in brackets — real money only, without bonus):

- **Bet / handle** — `casino_bet_amount_usd` (`casino_bet_amount_real_usd`)
- **Win / payouts** — `casino_win_amount_usd` (`casino_win_amount_real_usd`)
- **GGR** — `casino_ggr_usd` (`casino_ggr_real_usd`)
- **Bet count** — `casino_bet_count` (`casino_bet_count_real`)

## Metric definitions — from the platform catalog

Formulas come from the catalog (`list_metrics` / `query_metric`) under the rule of
`clickhouse-mart`, not from memory. Casino metrics of this mart carry the `_games` suffix
(`ggr_games`, `rtp_games`, …); prefer `query_metric` for them — both mandatory adjustments
are already built into the layer. This skill defines the mart specifics for manual SQL.
The building block for every manual GGR:

```sql
sum(if(project = '170', casino_ggr_real_usd, casino_ggr_usd))   -- always with WHERE project != '190'
```

## Examples

### 1. GGR by day and brand — canonical reconciliation with daily

```sql
SELECT
    date,
    company,
    round(sum(if(project = '170', casino_ggr_real_usd, casino_ggr_usd)), 2) AS ggr_usd
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
    round(sum(if(project = '170', casino_ggr_real_usd, casino_ggr_usd)), 2)               AS ggr_usd,
    round(sum(if(project = '170', casino_bet_amount_real_usd, casino_bet_amount_usd)), 2) AS bet_usd,
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
`game_provider_full_name` spread part of a real provider's GGR over other values. Say so
in the answer.

```sql
SELECT
    game_provider_full_name,
    round(sum(if(project = '170', casino_ggr_real_usd, casino_ggr_usd)), 2) AS ggr_usd,
    uniqExact(user_id)                                                      AS players
FROM demo.gaming_activity
WHERE date >= today() - 30
  AND date <  today()
  AND project != '190'
GROUP BY game_provider_full_name
ORDER BY ggr_usd DESC
LIMIT 20
```

### 4. Week over week GGR

For the catalog metric use two `query_metric` calls (see `clickhouse-mart`). Manual form:

```sql
SELECT
    sumIf(if(project = '170', casino_ggr_real_usd, casino_ggr_usd), date >= today() - 7)                         AS last_7d,
    sumIf(if(project = '170', casino_ggr_real_usd, casino_ggr_usd), date >= today() - 14 AND date < today() - 7) AS prev_7d,
    round(toFloat64(last_7d - prev_7d) / nullIf(toFloat64(prev_7d), 0) * 100, 2)                                                    AS delta_pct
FROM demo.gaming_activity
WHERE date >= today() - 14
  AND date <  today()
  AND project != '190'
```

### 5. Top games for a period

The result grain must match the question: "top games" = one row per `game_name`.
**Do not put `game_provider_full_name` into GROUP BY**: the field is not 1:1 with the
game, and the top silently turns into a top of game slices — GGR of one game spreads
below the LIMIT, aliases get lost. Give the provider as a reference column:

```sql
SELECT
    game_name,
    round(sum(if(project = '170', casino_ggr_real_usd, casino_ggr_usd)), 2)               AS ggr_usd,
    round(sum(if(project = '170', casino_bet_amount_real_usd, casino_bet_amount_usd)), 2) AS bet_usd,
    uniqExact(user_id)                                                                    AS players,
    groupUniqArray(game_provider_full_name)                                               AS providers  -- reference only
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

Apply both adjustments **always**, but **do not reveal internal project codes** to the
user: codes are not for every recipient. The adjustments are a detail of the query, not
part of the answer: keep them in SQL.

When answering over `gaming_activity`, state:

1. That the mandatory industry GGR adjustments were applied (in general terms, no
   codes). If you need to explain a difference with a naive number, say that some
   projects are computed on real-money GGR and some are excluded, without numbers.
2. That the mart covers casino only; cross-product numbers come from `demo.daily`.
3. Period and filters, as `clickhouse-mart` requires.

Where possible compute through `query_metric` (`*_games` metrics): there the adjustments
live in the metric layer and codes do not reach the output at all.
