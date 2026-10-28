---
name: domain-table-template
description: TEMPLATE for a domain skill covering one table - copy it to <domain>-analysis and fill it in. Rules and reference for the mart.<table> table - grain, fields, mandatory adjustments, ready-made example queries. Use when writing SQL against mart.<table> BY HAND - field breakdowns, top-N, reconciliation with other tables. For catalog metrics (metrics-catalog) this skill is needed only for caveats and adjustments not covered by the spec. Applies on top of warehouse-mart and does not override its rules.
---

<!--
How to use this template:
1. Copy the directory to skills/<domain>-analysis/, change name and description.
2. Keep only what the agent would get wrong on this table without it. The rest belongs in column COMMENTs.
3. Give every adjustment a ready-made SQL fragment: the agent copies examples verbatim.
4. Long reference material (all fields, example queries) goes to references/; keep SKILL.md short.
5. Below is a filled-in example for a hypothetical mart.sportsbook_bets table. Replace it with your own.
-->

# Sportsbook Bets - `mart.sportsbook_bets`

An add-on to `warehouse-mart`: its rules (`mart` only, `SELECT` only, date filter, meaning
from `COMMENT`) apply here too.

## Grain and scope

**One row per bet slip.** Sportsbook only; casino rounds are in `mart.casino_rounds`, player
totals (active players, deposits) - in `mart.player_daily`. A slip counts towards the day it was
settled (`settled_date`); unsettled slips have `status = 'open'` and no payout yet.

Money is in USD (`*_usd`), measures are `Nullable`: use `sum()` and `nullif()`, don't
treat NULL as zero by hand.

## Mandatory adjustments (always apply)

### 1. Source `<S2>` - real-money columns only

For source `<S2>` the standard money columns are empty (NULL); the `real_*` family is populated.
The substitution is needed **in every money aggregate**, otherwise the source silently drops
out of the sum:

```sql
CASE WHEN source = '<S2>' THEN real_stake_usd  ELSE stake_usd  END   -- stake
CASE WHEN source = '<S2>' THEN real_payout_usd ELSE payout_usd END   -- payout
```

Fixing one column and leaving the other raw is worse than not fixing anything: stakes and GGR
in the same answer stop adding up.

### 2. Brand `<T9>` - exclude entirely

```sql
WHERE brand != '<T9>'
```

Codes are strings; compare them with strings.

> Adjustments that hold for every metric of the table should be duplicated in
> `tables.<table>.where` in the metrics catalog - that way they aren't forgotten when
> computing per spec either.

## Fields

Dimensions: `bet_id`, `player_id`, `settled_date`, `country`, `platform`, `sport`, `league_id`,
`league_name` (**not 1:1 with `league_id`** - localized names of the same league; group by
`league_id`, show the name as a reference column), `bet_type` (`single` / `multi`), `status`.
Measures: `stake_usd` (`real_stake_usd`), `payout_usd` (`real_payout_usd`), `selections`.

## Examples

Ready-made queries with adjustments - [references/queries.md](references/queries.md).
The full column description is the table's `COMMENT`; only fields with pitfalls are listed here.

## What to say in the answer

1. That mandatory methodology adjustments were applied - generically, **without the codes** `<S2>`, `<T9>`.
2. That only settled slips are counted and the day is the settlement day.
3. Approximations (league names merged by `league_id`) - explicitly.
