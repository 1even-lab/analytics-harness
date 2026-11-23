---
name: gaming-activity-analysis
description: Rules and reference for the demo.gaming_activity casino table - grain, fields, the mandatory adjustment, ready example queries. Use when writing SQL against demo.gaming_activity BY HAND - GGR, handle, hold, RTP, players, games, providers, brands, reconciliation with demo.daily. For catalog metrics (metrics-catalog) the adjustment is already in the specs; this skill explains it and covers what a spec cannot. Applies on top of warehouse-mart and does not override its rules.
---

# Casino activity - `demo.gaming_activity`

An add-on to `warehouse-mart`: its rules (`demo` only, `SELECT` only, date filter, meaning
from `COMMENT`) apply here too.

## Grain and scope

**One row per player per day per game / provider / aggregator.** Casino only (slots, live,
crash, table games): no sportsbook, poker or payments. Cross-product numbers and the daily
P&L are in `demo.daily`.

Money is in USD, `Decimal(18, 2)`: `casino_bet_amount_usd` (handle), `casino_win_amount_usd`
(payouts), `casino_ggr_usd` (bet - win). Ratios divide `toFloat64` (see `warehouse-mart`).

## Mandatory adjustment (always apply)

### Project `190` - exclude entirely

```sql
WHERE project != '190'
```

In every sample, aggregate and metric over this table: the project is not part of the
business. `project` is a string code: compare it with strings. The rule is also in
`tables.demo.gaming_activity.where` of the metrics catalog.

## Fields with pitfalls

- `game_provider` is **not 1:1 with the game**: one game shows up under provider aliases
  (`Skyline Studio` / `Skyline` / `Undefined`), and the aggregator name `HubX` leaks into the
  provider field. Never `GROUP BY` it in a game top; give it as a reference column
  (`groupUniqArray`). Provider rankings are approximate - say so.
- The same `game_name` at different providers can be a different game (live tables such as
  `Dragon Tiger Live`): if `providers` of a game has several values, check and say which.
- Days with no rows for a brand are missing data, not zero activity.

Everything else is in the column `COMMENT`s.

## Examples

Ready-made queries with the adjustment applied - [references/queries.md](references/queries.md).

## What to say in the answer

1. That the mandatory methodology adjustment was applied - generically, **without the code**
   `190`: it stays in SQL.
2. That the table covers casino only; cross-product numbers come from `demo.daily`.
3. Approximations (provider cuts) and gaps (missing days) - explicitly.
