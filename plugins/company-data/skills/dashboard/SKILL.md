---
name: dashboard
description: "A dashboard or chart on <Company> data: where to deliver it, how to take numbers from metrics already computed without recomputing, and what it looks like in the brand style. ALWAYS use when asked for a dashboard, chart, visualization, 'show the trend / compare on a chart', or when an answer is better shown than told. Does NOT describe visualization mechanics (choice of chart form, palettes, labels) - those live in general visualization skills; this covers only what they can't know."
---

# Dashboard - what a general visualization skill doesn't know

Chart form, labels, legends, filters - from a general visualization skill, if available.
This covers three things: **where it goes**, **where the numbers come from**, **what the brand
looks like**.

## 1. Where it goes

| The user wants | Path |
|---|---|
| to look now, "show me", "dashboard" with no detail | **HTML artifact** (default) - scaffold below |
| the team to open it themselves, with filters, "in BI" | skill `bi-reporting` |
| regular delivery to a channel / email | not done by the agent - suggest a task for data engineers |

"Dashboard" is already a format - **don't ask again**, and don't ask where to deliver it:
without the words "BI", "for the team" or "with filters" it is an HTML artifact. You may clarify
only the period and the breakdown, in one question, if they are neither in the question nor in
the conversation.

**No data access** (`data-router`, section C) - still build the HTML scaffold: every KPI and
chart gets a placeholder instead of a number and the SQL that fills it, compiled per
`metrics-catalog`. Never put plausible-looking sample numbers into it.

## 2. Where the numbers come from

**First, what's already in the conversation.** Metrics computed in this chat are the dashboard's
data. Before recomputing, check: same metrics, same period, the needed breakdown is there, the
result isn't cut off by `LIMIT`. Fetch **only what's missing**.

**No data yet** - compute per `metrics-catalog`, all independent queries in one turn: totals
for KPIs (a separate query with no breakdown - the sum of points is not a total) and one query
per breakdown.

| On the dashboard | From |
|---|---|
| metric label | `title` from the catalog, don't rewrite |
| number format | `unit`: `USD` → `$1.2M`, `count` → `12.9K`, `pct` → `3.42%` |
| KPIs | a separate query with no breakdown |
| caveats | the `caveat` of every metric shown |

**A filter in the artifact only slices what was computed.** Need a country filter - country must
be in the query's breakdown. Ratios and averages aren't recomputed under a filter by adding up -
either one query per slice or no filter on them.

**A derived value outside the catalog** is labeled ("outside the catalog, formula: ...") or not shown.

## 3. What the brand looks like

Scaffold - [references/dashboard-starter.html](references/dashboard-starter.html): tokens,
components, a Chart.js preset, the caveats block. Copy it and replace the content.

What must not change:
- Palette - only the scaffold's tokens: background, surface, **one accent** `--accent`, second
  series `--series-2`. There is no third color - **never more than two series per chart**:
  the rest goes into separate charts or a table.
- Deltas: growth in the accent with ▲, decline muted with ▼. No red-green pair.
- Fonts - from the scaffold, with a system fallback.
- No emoji; the headline is a short statement, not a slogan.
- One external resource - Chart.js from `cdn.jsdelivr.net/npm`. CSS is inline.

## 4. The "Source and caveats" block is mandatory

As the last block: metrics (`title`), period and comparison window, data freshness, caveats.
Don't show internal codes or adjustment details: "mandatory methodology adjustments applied".

## 5. Before handing over
1. Every number was computed per catalog (or labeled as outside the catalog).
2. The period and caveats in the block match the computation.
3. Names are canonical `title`s; no codes.
4. No charts with three or more series, no second accent, no emoji.
5. Three lines in the reply: what is shown, for what period, where the caveats are.
