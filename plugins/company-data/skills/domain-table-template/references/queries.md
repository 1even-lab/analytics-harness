# Example queries for `mart.sportsbook_bets`

All examples already include the mandatory adjustments from SKILL.md. The agent copies them
verbatim: add a new example only after verifying it on real data.

## Sportsbook GGR by day (with adjustments)
```sql
SELECT
    settled_date
    , round(sum(CASE WHEN source = '<S2>' THEN real_stake_usd ELSE stake_usd END)
          - sum(CASE WHEN source = '<S2>' THEN real_payout_usd ELSE payout_usd END), 2) AS ggr_usd
FROM mart.sportsbook_bets
WHERE settled_date >= CURRENT_DATE - INTERVAL '30' DAY
  AND settled_date <  CURRENT_DATE
  AND status = 'settled'
  AND brand != '<T9>'
GROUP BY settled_date
ORDER BY settled_date
```

## Top leagues by stake
One row per `league_id`; `league_name` is for reference, not a grouping key:
```sql
SELECT
    league_id
    , min(league_name) AS league_name
    , round(sum(CASE WHEN source = '<S2>' THEN real_stake_usd ELSE stake_usd END), 2) AS stake_usd
    , count(DISTINCT player_id) AS players
FROM mart.sportsbook_bets
WHERE settled_date >= CURRENT_DATE - INTERVAL '30' DAY
  AND settled_date <  CURRENT_DATE
  AND status = 'settled'
  AND brand != '<T9>'
GROUP BY league_id
ORDER BY stake_usd DESC
LIMIT 30
```
