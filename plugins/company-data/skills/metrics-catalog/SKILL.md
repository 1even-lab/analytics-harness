---
name: metrics-catalog
description: The <Company> metrics catalog - the single source of formulas, mandatory filters and caveats. ALWAYS use when you need to compute, explain or compare a business metric (GGR, rounds, average bet, active players, depositors, ARPU, retention, etc.), build a KPI, a report or a dashboard. Tells where the specs live (references/metrics.yaml) and how to compile a spec into SQL so the number matches the official one.
---

# Metrics catalog

Metric definitions live in [references/metrics.yaml](references/metrics.yaml); the format and
compilation rules are in [references/spec-format.md](references/spec-format.md). There is no
server that compiles SQL for you: **you compile the spec yourself**, and every condition you
drop is on you.

## Workflow

1. **Find the metric** in `metrics.yaml` - by key, `title`, `description` or synonyms.
   - Several similar ones - show the candidates (`title` + `description`); don't pick silently.
   - Not found - say so directly and suggest the closest ones. Don't invent a formula; if the
     metric is needed once - agree on the formula with the user and label the result
     "outside the catalog".
2. **Check the breakdown:** the requested dimension must be in the metric's `dims`. If it isn't,
   the metric has no such slice; say so, don't substitute a column yourself.
3. **Compile SQL per `spec-format.md`:** `expression` from `table`, window on `time_column`,
   **all** filters (`tables.<table>.where` + the metric's `where`), `dims` by alias,
   `final` / `dedup` if set.
4. **Run it** through the warehouse connector. For a heavy query, try a single date first.
5. **Return the result** per `basic-analytics`: the metric's `title`, `unit`, period, window
   freshness and **the `caveat`, faithfully**, if there is one.

## Hard rules

- **Filters are never relaxed.** Dropping a condition from `where` "to match the dashboard" is
  not allowed: the discrepancy is a finding - show both numbers.
- **Metrics with different `table`s are not added or divided** in one query without reducing
  them to a common grain. Need a derived value (GGR / active players from different tables) -
  compute each per its own spec, combine the results, and label the derived value.
- **Ratios and averages (`unit: pct`, `ratio`) are not summed** across rows and periods:
  recompute per spec for each window or slice.
- **Period comparison** - two computations per spec with windows of equal length, not the
  difference of daily rows.
- **Show the SQL if asked or if the number is disputed** - it must be reproducible.

## Checklist before answering
- [ ] The metric was found in the catalog (or explicitly labeled "outside the catalog").
- [ ] The SQL contains **every** condition from `tables.<table>.where` and the metric's `where`.
- [ ] Breakdowns come only from `dims`; `dedup` / `final` are handled.
- [ ] The window is on `time_column`, freshness checked.
- [ ] The answer has `title`, `unit`, period, `caveat`.
