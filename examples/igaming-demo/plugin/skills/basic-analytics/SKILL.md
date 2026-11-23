---
name: basic-analytics
description: Cross-cutting rules for presenting analytics on any request for a report, summary, export, analysis, dashboard or data visualization. ALWAYS use when the user asks to compute, summarize, analyze or show data, especially if they haven't specified the output format or parameters. Defines when and how to briefly ask about format, period, breakdown and metrics, and the common styling rules for results. Works ON TOP of the data skills (metrics-catalog, warehouse-mart, domain skills) and does not replace their rules.
---

# Basic Analytics - presentation and interaction

This layer is about **how** to deliver analytics, not **where** data comes from. Sources and
formulas live in `metrics-catalog`, `warehouse-mart` and the domain skills.

## Rule 1. Ask about the format only if it isn't given

If the format is named - including words like "dashboard", "chart", "show the trend" - **don't
ask again**: "dashboard" with no other detail = an HTML artifact per the `dashboard` skill.
No format and it isn't obvious from context - **one** short question with options:

- **Table in chat** - a one-off look.
- **Chart** - trend, comparison, shares.
- **Slide** - if the result goes into a presentation (skill `pptx`).
- **Text summary** - conclusions in words with key numbers.
- **Excel / CSV** - to keep working with the data yourself (skill `xlsx`).
- **Dashboard** - one-off HTML (`dashboard`); there is no BI tool in this demo.

No answer - default: a short summary with one table.

## Rule 2. Don't over-ask

At most one round, 1-3 questions, only about what is missing:
- **Period** - default is the last 30 full days; state the window in the answer.
- **Breakdown** - by day, country, platform, game, provider...
- **Metrics** - canonical names from the catalog.

## Rule 3. Result styling

- **Answer first, then details** - the key number or conclusion in the first line.
- **Label** currency, period, units, % for shares.
- **Round** money sensibly; large numbers - `1.2M`, `12.9K`.
- **Source and filters**: which table, period, what was applied. Don't show internal
  identifiers (tenant codes, ids of excluded segments) to recipients - phrase it generically
  ("mandatory methodology adjustments applied").
- **Flag anomalies and NULLs**; don't present an unvalidated number as fact.
- **Metric names - canonical `title` from the catalog**; a plain-language gloss may go next to it.
- **A derived value outside the catalog** is either labeled ("outside the catalog, formula: ...")
  or not shown. Needed regularly - suggest adding a spec to `metrics.yaml`.
- **Period comparison - for every row of the table**, or say explicitly why a row doesn't have it.
- **Caveats (`caveat`)** of every metric shown go into the answer, not "somewhere in the spec".

## Rule 4. Format → tool

| Requested | Use |
|---|---|
| Presentation / slides | skill `pptx` |
| Excel / CSV / "export" | skill `xlsx` |
| One-off dashboard / chart in the answer | skill `dashboard` |
| Regular delivery to a channel | not done by the agent: suggest a task for data engineers |
| Table / text | directly in the answer |
