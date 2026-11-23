# Example queries for `demo.gaming_activity`

Both mandatory adjustments are applied in every query. The agent copies these verbatim, so a
broken example spreads into every answer: change them with the same care as a metric spec.

## 1. GGR by day and brand - reconciliation with daily

```sql
SELECT
    date,
    company,
    round(sum(if(project = '170', casino_ggr_real_usd, casino_ggr_usd)), 2) AS ggr_usd
FROM demo.gaming_activity
WHERE date >= '2026-10-01'
  AND date <  '2026-11-01'
  AND project != '190'
GROUP BY date, company
ORDER BY date, ggr_usd DESC
```

The same per brand and day from `demo.daily` (`sum(casino_ggr_usd)`) must match.

## 2. GGR, handle, hold and players by brand

```sql
SELECT
    company,
    round(sum(if(project = '170', casino_ggr_real_usd, casino_ggr_usd)), 2)               AS ggr_usd,
    round(sum(if(project = '170', casino_bet_amount_real_usd, casino_bet_amount_usd)), 2) AS bet_usd,
    round(ggr_usd / nullIf(bet_usd, 0) * 100, 2)                                          AS hold_pct,
    uniqExactIf(user_id, if(project = '170', casino_bet_amount_real_usd, casino_bet_amount_usd) > 0) AS active_players
FROM demo.gaming_activity
WHERE date >= '2026-10-01'
  AND date <  '2026-11-01'
  AND project != '190'
GROUP BY company
ORDER BY ggr_usd DESC
```

## 3. Top providers by GGR (approximate)

```sql
SELECT
    game_provider_full_name,
    round(sum(if(project = '170', casino_ggr_real_usd, casino_ggr_usd)), 2) AS ggr_usd,
    uniqExact(user_id)                                                      AS players
FROM demo.gaming_activity
WHERE date >= '2026-10-01'
  AND date <  '2026-11-01'
  AND project != '190'
GROUP BY game_provider_full_name
ORDER BY ggr_usd DESC
LIMIT 20
```

Say in the answer that aliases and the aggregator name spread part of a provider's GGR.

## 4. Top games - one row per game, provider as reference

```sql
SELECT
    game_name,
    round(sum(if(project = '170', casino_ggr_real_usd, casino_ggr_usd)), 2)               AS ggr_usd,
    round(sum(if(project = '170', casino_bet_amount_real_usd, casino_bet_amount_usd)), 2) AS bet_usd,
    uniqExact(user_id)                                                                    AS players,
    groupUniqArray(game_provider_full_name)                                               AS providers  -- reference only
FROM demo.gaming_activity
WHERE date >= '2026-10-01'
  AND date <  '2026-11-01'
  AND project != '190'
GROUP BY game_name
ORDER BY ggr_usd DESC
LIMIT 30
```

## 5. Days with no rows for a brand

```sql
SELECT
    company,
    arrayFilter(d -> NOT has(days, d),
                arrayMap(i -> toDate('2026-10-01') + i, range(31))) AS missing_days
FROM
(
    SELECT company, groupUniqArray(date) AS days
    FROM demo.gaming_activity
    WHERE date >= '2026-10-01'
      AND date <  '2026-11-01'
      AND project != '190'
    GROUP BY company
)
WHERE length(missing_days) > 0
```
