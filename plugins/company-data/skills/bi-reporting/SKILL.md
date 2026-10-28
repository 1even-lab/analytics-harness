---
name: bi-reporting
description: "Rules for the <BI> BI tool - finding and reading published reports, creating and editing cards and dashboards. ALWAYS use when asked for data 'from BI / from the dashboard / from the report', when reconciling numbers with a published report, or when a result must be delivered into BI. BI is delivery and a showcase for people, not a source of methodology: formulas come from metrics-catalog, presentation from basic-analytics."
---

# BI Reporting

BI shows what has been computed but doesn't define how to compute it. What and how to compute
is `metrics-catalog` and the domain skills; this skill is about reading BI and getting a number
into a card correctly. Datasources, ids, data windows and MCP tools of a specific BI tool are in
[references/bi-tool-template.md](references/bi-tool-template.md) (one file per tool).

## Reading

1. **Approved sources only.** First call - list datasources tagged `<AI / certified>`. Don't
   use untagged ones, even if they are visible. Empty list - the message below and stop.
2. **Field meaning comes from datasource metadata and the table `COMMENT`**, not from memory.
3. **Data window:** <e.g. the `player_daily` datasource holds only the last <N> months> - go to
   the warehouse for older history.
4. **Additive metrics** are aggregated with `SUM` over dates; ratios and averages only from the
   report itself or recomputed per catalog, never by arithmetic over rows.

## Writing (if the connector allows it)

1. **Search first, then create.** A card with the same meaning exists - update it instead of
   creating a duplicate. Duplicates with slightly different formulas are the main source of
   "two different revenues".
2. **Card data - `mart.*` only.** No `raw`, `staging`, `sandbox` or legacy databases
   (`<legacy connection name>`).
3. **The number must match the catalog.** Before saving, compute the same metric per spec for
   the same period. A discrepancy - stop and show both SQL queries.
4. **Domain skill adjustments go into the card's SQL.** A card without them is a wrong report
   that lives forever and spreads via screenshots.
5. **Ask for the collection** if it isn't named; don't put cards in the root.
6. **A card description is mandatory:** the table, hard-coded filters and period, the catalog
   metric by name. No live business numbers in titles.

## Messages

BI unavailable:
```
The BI connector is unavailable. Check that it is connected: Settings → Connectors → "<BI>".
```
No approved datasources:
```
There are no datasources tagged "<AI>". You need access to them or the tag on the right datasource - ask the BI owner.
```
