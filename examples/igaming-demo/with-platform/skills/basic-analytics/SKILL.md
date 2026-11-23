---
name: basic-analytics
description: Cross-cutting rules for delivering analytics and talking to the user, for any request for a report, summary, export, analysis, dashboard or chart. Use ALWAYS when the user asks to compute, summarize, analyse or show data, especially when the form or parameters are not given. Sets when and how to ask briefly about the format (table, chart, slide, text summary, CSV / Excel, HTML dashboard), period, breakdown and metrics, fixes common presentation rules and how to set up a regular digest. Works ON TOP of the data skills (clickhouse-mart, gaming-analysis) and does not replace their rules on sources and metrics.
---

# Basic Analytics — delivery and interaction

A cross-cutting layer about **how** to deliver analytics, not **where** the data comes
from. Sources, metrics and adjustments are in `clickhouse-mart` and `gaming-analysis`;
this skill does not override them.

## When to apply

Any request for a "report", "summary", "analysis", "breakdown", "export", "dashboard",
"show / compute / compare data" — even if no format is named.

## Rule 1. Ask about the form if it is not given

Before building a report make sure the **result format** is clear. If it is named —
including words like "dashboard", "chart", "show the trend" — do not ask again. Only if
the user gave no format and context does not make it obvious, ask **one short question**
with options:

- **Table in the chat** — a quick one-off look.
- **Chart** — trend, comparison, shares.
- **Slide** — if the result goes into a presentation.
- **Text summary** — conclusions in words with the key numbers.
- **CSV / Excel file** — to keep working with the data.
- **Dashboard** — several metrics and charts in one HTML page.

"Summary", "nice", "compact" are not a format: people use them for a Slack message, a
picture, a dashboard and a slide alike. If the channel is not named, ask once with these
options. With still no format, a sensible default is a short text summary with one table.

## Rule 2. Do not over-ask

Ask **only what is missing**, at most one round (1–3 questions). Besides the format,
check whether these are given:

- **Period** (default — the last 30 days, as in `clickhouse-mart`).
- **Breakdown / grain** (brand, geo, game, provider, day, player…).
- **Metrics** (GGR, hold, active players, ARPPU…).

If only the form is unclear, ask only about the form.

## Rule 3. Common presentation rules

Whatever the form:

- **Answer first, details after** — the key number or conclusion in the first line.
- **Label**: currency (USD), period, units, % for shares.
- **Round** money sensibly; big numbers readable (k / M).
- **Name the source and filters**: which mart, which period, that the mandatory
  adjustments were applied. **Do not reveal internal project codes** — they are not for
  every recipient; mention adjustments in general terms. Prefer `query_metric`: there the
  adjustments live in the layer and codes never reach the answer.
- **Flag anomalies, NULLs and missing days**; do not present unvalidated numbers as fact.
- **Call metrics by their catalog titles** (`title` from `list_metrics`, e.g. `$ GGR`,
  `% Hold`) so the recipient can match the line with the catalog.
- **Nothing outside the catalog in a table of catalog metrics**: a value computed by your
  own formula is either labelled ("outside the catalog, formula: …") or not shown.
- **Period comparison for every row.** If you show WoW / MoM, show it for each metric
  (two `query_metric` calls per metric, see `clickhouse-mart`) or say why it is missing.

## Rule 4. Format → tool

| Asked for | How |
|---|---|
| Table / text | right in the answer |
| Chart, dashboard | one HTML page |
| CSV / Excel | a file |
| Regularly to a channel or a DM | a platform schedule — rule 5 |

## Rule 5. Regular digest

- **Catalog numbers — a `metric_digest` subscription.**
  `create_schedule(task_type='metric_digest', parameters={calls: [query_metric arguments
  as in the chat], brief: how to present}, delivery_target='slack:me' or
  'slack:<channel>')`, then `run_schedule_now(job_id)`: the first issue arrives at once.
  Window `last_n_days` only, up to 6 calls and up to 12 metrics per call, `brief` up to
  1500 characters. Differences and % are computed by the platform; the model only writes
  the text.
- **`analysis` — only for data outside the catalog.** It does not call `query_metric` and
  needs ready SQL under the rules of `clickhouse-mart`. Do not rebuild a catalog metric by
  hand in it: when the catalog adjustments change, the digest silently drifts away.
- No project codes and no adjustment details in `brief` or in the message.

## What this skill does NOT do

It does not decide where the data comes from or how metrics are computed. With
ClickHouse the rules of `clickhouse-mart` always apply (`demo` only, read-only, field
meaning from `COMMENT`, metric definitions from the platform catalog), and for the casino
vertical — `gaming-analysis`.
