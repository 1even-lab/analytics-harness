---
name: data-router
description: "Entry point for working with the iGaming demo data. ALWAYS use when a question concerns the demo brands' data - analytics, reports, metrics, KPIs, GGR, handle, hold, RTP, players, deposits, registrations, games, providers, the warehouse / DWH / the demo database, dashboards, exports. Decides where data comes from and which skills apply: with the warehouse connector - compute from metric specs; without one - methodology only, no numbers."
---

# iGaming demo data

The warehouse is the `demo` database in ClickHouse: `demo.gaming_activity` (casino, one row
per player per day per game) and `demo.daily` (brand x day across products). Brands, players
and numbers are fictional.

## Step 0. Check what is connected

Check whether the `clickhouse` MCP connector of this plugin is available and answers a
simple query (`SELECT 1`). Everything else depends on this - don't skip it.

| what is connected | go to |
|---|---|
| **warehouse connector** | **section A** - full analytics |
| nothing | **section C** - methodology only, no numbers |

There is no BI tool in this demo, so the template's section B is not used.

---

## A. Warehouse connector available

1. **The metric in the question is in the catalog** → skill `metrics-catalog`: formula, filters
   and caveats come from `metrics.yaml`, SQL is compiled from the spec. This is the default path.
2. **The metric is not in the catalog, or an ad-hoc slice is needed** → skill `warehouse-mart`
   (rules for hand-written SQL) plus `gaming-activity-analysis` for anything on
   `demo.gaming_activity`.
3. **Answer format** → `basic-analytics`, in the same turn as everything else.
4. **Dashboard, chart, "show the trend"** → the format is already named, don't ask again;
   skill `dashboard`. Numbers already computed in this conversation are the dashboard's data:
   fetch only what is missing.

**You read under the connector's role, not the recipient's.** Before sending a result to a
shared channel or outside, consider whether every recipient is entitled to that data.

**The connector responds but queries fail on authorization** - that is no reason to look for
workarounds. Tell the user that the warehouse credentials in their environment
(`CLICKHOUSE_USER` / `CLICKHOUSE_PASSWORD`) are not accepted, and stop.

---

## C. Nothing connected

You can only help with methodology: explain how a metric is computed per `metrics-catalog`,
walk through the formula, prepare SQL for the person to run themselves.

**Don't state numbers** - not from memory, not "roughly", not "on the order of". A plausible
number without a source is worse than an honest refusal: it will be carried into a decision and
nobody will remember where it came from.

**Asked for a dashboard or chart without data** - still use the `dashboard` skill: deliver the
HTML scaffold with one SQL query per block and placeholders instead of numbers.

If data is needed - set `CLICKHOUSE_HOST` and `CLICKHOUSE_PASSWORD` in the environment and
restart Claude (see the example's README).
