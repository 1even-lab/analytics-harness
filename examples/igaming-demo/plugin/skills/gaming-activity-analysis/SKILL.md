---
name: gaming-activity-analysis
description: Rules and reference for the demo.gaming_activity casino table - grain, fields, the mandatory GGR adjustments, ready example queries. Use when writing SQL against demo.gaming_activity BY HAND - GGR, handle, hold, RTP, players, games, providers, brands, reconciliation with demo.daily. For catalog metrics (metrics-catalog) the adjustments are already in the specs; this skill explains them and covers what a spec cannot. Applies on top of warehouse-mart and does not override its rules.
---

# Casino activity - `demo.gaming_activity`

An add-on to `warehouse-mart`: its rules (`demo` only, `SELECT` only, date filter, meaning
from `COMMENT`) apply here too.

## Grain and scope

**One row per player per day per game / provider / aggregator.** Casino only (slots, live,
crash, table games): no sportsbook, poker or payments. Cross-product numbers and the daily
P&L are in `demo.daily`.

Money is in USD (`*_usd`), measures are `Nullable`: use `sum()` and `nullIf()`, don't treat
NULL as zero by hand.

## Mandatory adjustments (always apply)

### 1. Project `170` - real-money columns only

Project `170` has **all standard money columns empty (NULL)**, not just GGR: only the
real-money family is filled. Summing the standard columns silently drops the project, so the
substitution goes into **every money aggregate**:

```sql
if(project = '170', casino_ggr_real_usd, casino_ggr_usd)                 -- GGR
if(project = '170', casino_bet_amount_real_usd, casino_bet_amount_usd)   -- handle
if(project = '170', casino_win_amount_real_usd, casino_win_amount_usd)   -- payouts
```

Fixing GGR and reading handle raw is worse than not fixing anything: the project is in GGR and
missing from handle, so hold and RTP in the same answer stop agreeing.

**Project `170` has no bet counter in any form** (`casino_bet_count` NULL,
`casino_bet_count_real` zero). The number of bets is not computed for it, and "was active" is
taken from handle: `coalesce(casino_bet_count, 0) > 0` removes every player of the project.

### 2. Project `190` - exclude entirely

```sql
WHERE project != '190'
```

In every sample, aggregate and metric over this table. `project` is a string code: compare it
with strings. The rule is also in `tables.demo.gaming_activity.where` of the metrics catalog.

## Fields with pitfalls

- `game_provider_full_name` is **not 1:1 with the game**: one game shows up under provider
  aliases (`Skyline Studio` / `Skyline` / `Undefined`), and the aggregator name `HubX` leaks
  into the provider field. Never `GROUP BY` it in a game top; give it as a reference column
  (`groupUniqArray`). Provider rankings are approximate - say so.
- The same `game_name` at different providers can be a different game (live tables such as
  `Dragon Tiger Live`): if `providers` of a game has several values, check and say which.
- Days with no rows for a brand are missing data, not zero activity.

Everything else is in the column `COMMENT`s.

## Examples

Ready-made queries with the adjustments applied - [references/queries.md](references/queries.md).

## What to say in the answer

1. That mandatory methodology adjustments were applied - generically, **without the codes**
   `170`, `190`: they stay in SQL.
2. That the table covers casino only; cross-product numbers come from `demo.daily`.
3. Approximations (provider cuts) and gaps (missing days) - explicitly.
