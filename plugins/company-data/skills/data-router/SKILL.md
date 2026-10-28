---
name: data-router
description: "Entry point for working with <Company> data. ALWAYS use when a question concerns company data - analytics, reports, metrics, KPIs, GGR, bets, players, deposits, the warehouse / DWH / mart tables, BI, dashboards, exports. Decides where data comes from and which skills apply: with a warehouse connector - compute from metric specs; without one - methodology only, no numbers."
---

# <Company> data

## Step 0. Check what is connected

Check whether the warehouse MCP connector (`<warehouse-mcp>`) is available and answers a
simple query. Everything else depends on this - don't skip it.

| what is connected | go to |
|---|---|
| **warehouse connector** | **section A** - full analytics |
| no warehouse, but a **BI connector** (`<bi-mcp>`) | **section B** - published reports only |
| nothing | **section C** - methodology only, no numbers |

---

## A. Warehouse connector available

1. **The metric in the question is in the catalog** → skill `metrics-catalog`: formula, filters
   and caveats come from `metrics.yaml`, SQL is compiled from the spec. This is the default path.
2. **The metric is not in the catalog, or an ad-hoc slice is needed** → skill `warehouse-mart`
   (rules for hand-written SQL) plus the table's domain skill, if there is one (`<domain>-analysis`).
3. **Answer format** → `basic-analytics`, in the same turn as everything else.
4. **Dashboard, chart, "show the trend"** → the format is already named, don't ask again;
   skill `dashboard`. Numbers already computed in this conversation are the dashboard's data:
   fetch only what is missing.

**You read under the connector's role, not the recipient's.** Before sending a result to a
shared channel or outside, consider whether every recipient is entitled to that data.

**The connector responds but queries fail on authorization** - that is no reason to look for
workarounds. Tell the user:

> The warehouse connector is not authorized. Reconnect it: **Settings → Connectors**,
> find "<warehouse-mcp>", Disconnect → Connect.

---

## B. BI only

Data comes only from published reports and datasources, per the `bi-reporting` skill.
Numbers may be stated, but with a source: "per dashboard <name>, period <...>".

- Don't derive "in your head" slices that aren't in the report from the visible numbers.
- Don't sum or average ratios and means across report rows.
- A metric that isn't in BI needs warehouse access - say so.

---

## C. Nothing connected

You can only help with methodology: explain how a metric is computed per `metrics-catalog`,
walk through the formula, prepare SQL for the person to run themselves.

**Don't state numbers** - not from memory, not "roughly", not "on the order of". A plausible
number without a source is worse than an honest refusal: it will be carried into a decision and
nobody will remember where it came from.

**Asked for a dashboard or chart without data** - still use the `dashboard` skill: deliver the
HTML scaffold with one SQL query per block and placeholders instead of numbers. The format is
already named - don't ask where to deliver it or in what form.

If data is needed - connect the warehouse connector (Settings → Connectors) or request access
from the DWH owner (`<contact>`).
