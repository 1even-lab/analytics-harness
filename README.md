# Analytics harness for Claude - example

A set of Claude skills plus a semantic metrics layer for working with company data: reports,
metrics, exports, dashboards, BI. Built for a team **without its own agent platform**: metric
definitions, mandatory filters and presentation rules ship together with the skills, and Claude
reads data through a regular MCP connector to the warehouse.

Everything in angle brackets (`<...>`) is a placeholder. Examples use a hypothetical iGaming
`mart.*` layer - casino rounds, player days, sportsbook bets, marketing campaigns; replace the
dialect, tables and metrics with your own.

The reasoning behind the layout is in [docs/DESIGN.md](docs/DESIGN.md): the problems the harness
answers, its two principles and which layer owns what.

A working instance - the template filled in for a ClickHouse warehouse you can load yourself,
with deterministic demo data and evals against its traps - is in
[examples/igaming-demo](examples/igaming-demo/README.md).

## What's inside

```
.claude-plugin/marketplace.json        marketplace: where the org installs the plugin from
plugins/company-data/
  .claude-plugin/plugin.json           plugin manifest (bump version = update for everyone)
  skills/
    data-router/                       entry point: what's connected → where rules and data come from
    basic-analytics/                   how to present an answer: format, clarifying questions, styling
    warehouse-mart/                    how to read the warehouse: mart layer, COMMENT, safe SQL
      references/messages.md           standard messages to the user
    metrics-catalog/                   semantics: metric specs and how to compile them into SQL
      references/metrics.yaml          ← the single source of formulas
      references/spec-format.md        spec format and SQL compilation rules
    domain-table-template/             template skill for one table with pitfalls (sportsbook bets)
      references/queries.md            example queries with adjustments applied
    dashboard/                         where a dashboard goes, where numbers come from, styling
      references/dashboard-starter.html
    bi-reporting/                      cards and dashboards in the BI tool
      references/bi-tool-template.md   datasources, ids, data windows, tools - one file per BI tool
  evals/                               behavioral cases for claude plugin eval + golden set
scripts/validate_metrics.py            metrics.yaml check before merge
```

## How it works

```
user question
  → data-router         is there a warehouse connector? (A: yes / B: BI only / C: nothing)
  → basic-analytics     answer format, period, breakdown - at most one round of questions
  → metrics-catalog     metric exists in metrics.yaml → SQL is compiled from the spec
  → warehouse-mart      no such metric or ad-hoc slice → rules for hand-written SQL on mart
  → domain-*            table with its own pitfalls → mandatory adjustments
  → dashboard / bi-reporting / xlsx / pptx   delivery
```

Skills refer to each other by name; Claude loads the relevant ones by their `description` in
the frontmatter, so descriptions are written as triggers: "ALWAYS use when...".

## What replaces the platform

With an agent platform, some rules are enforced by the server; here Claude enforces them from
the skill text, so the wording is stricter and repeated in checklists.

| with a platform | here |
|---|---|
| server-side metrics catalog compiles SQL from the spec | `metrics-catalog`: Claude reads `metrics.yaml` and compiles SQL itself per `spec-format.md` |
| server injects mandatory filters into SQL | `tables.<t>.where` + metric `where`; "all filters in SQL" checklist before answering |
| `caveat` arrives together with the rows | Claude must surface the `caveat` in the answer itself |
| gateway: a single `SELECT` only, scenario role | read-only DB user in the MCP connector + "SELECT only" rule in the skill |
| rule sets are loaded fresh from the server | skills live in the plugin; update = bump `version` and merge into the marketplace |
| catalog validation on sync | `scripts/validate_metrics.py` in marketplace CI |
| scheduled tasks with delivery to a channel | out of scope: tell the user it needs a pipeline from data engineers |

**The main risk without a platform:** the agent may "forget" a mandatory filter. Therefore
(1) filters shared by a table are written once in `tables.<t>.where`, not in every metric;
(2) where possible, move them into the warehouse itself - a row policy or a view - so they
physically cannot be forgotten.

## How to adopt

1. Create your marketplace repository (e.g. `<org>/claude-plugins`) from this template -
   **Use this template** on GitHub - or copy `.claude-plugin/marketplace.json`,
   `plugins/company-data/` and `scripts/` into an existing one.
2. Rename `company-data` and the skills, fill in the placeholders:
   - `metrics-catalog/references/metrics.yaml` - your metrics (start with 5-10 key ones);
   - `domain-table-template` - copy one skill per table that has pitfalls;
   - `dashboard` - brand tokens in `dashboard-starter.html`;
   - `bi-reporting` - your BI tool and its rules; delete what you don't need.
3. Add the marketplace:
   - **claude.ai / Desktop / Cowork:** Organization settings → Plugins → add marketplace;
   - **Claude Code:** `/plugin marketplace add <org>/claude-plugins`, then
     `/plugin install company-data@<marketplace-name>`.
4. Warehouse connector: your DB's MCP server with a **read-only user** that has grants only on
   `mart` and dictionaries. DB permissions are the real boundary; skill text is not.
5. Run 10-20 typical analyst questions and reconcile the numbers with BI. Every mistake is a
   fix to a metric spec, a `caveat` or a domain skill.

## Why `references/`

`SKILL.md` is loaded into context in full as soon as the skill fires; files in `references/`
are opened by link only when needed. So `SKILL.md` holds rules and workflow (short, always
needed), and `references/` holds what is long or changes more often: metric specs, SQL
examples, datasource ids, the HTML scaffold. Rule of thumb - `SKILL.md` under ~150 lines.

## Evals

`plugins/company-data/evals/` - details in [its README](plugins/company-data/evals/README.md).
- **Behavioral cases** (`claude plugin eval`) run without data: they check that the agent
  doesn't state numbers without a source, doesn't drop mandatory filters from SQL, doesn't
  slice a metric by a disallowed dimension, doesn't sum non-additive metrics, doesn't agree to
  modify data, and that the skills don't fire on unrelated questions. Run on every PR.
- **Golden set** - typical questions with reference numbers signed off by the metric owner.
  Run with a real connector before releasing a version.

## Maintenance

- A change to a formula or filter = a PR to the marketplace with review: a formula is methodology.
- Marketplace CI: `validate_metrics.py` and `claude plugin eval` on the behavioral cases.
- A defect found in an answer becomes a new case in `evals/` so it doesn't come back.
- After merge, bump `version` in `plugin.json`, otherwise clients won't pick up the changes.
- Found a data pitfall - in the same PR: the metric's `caveat` and/or the domain skill. The
  agent copies SQL examples from skills verbatim, so a broken example spreads into every report.
- `COMMENT`s on mart tables and columns are part of the harness: `warehouse-mart` doesn't work
  without them.

## Licence and author

MIT, see [LICENSE](LICENSE). Written by Max Ivanov, 1even.lab.
