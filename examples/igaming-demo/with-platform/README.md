# The same warehouse, with an agent platform

`../plugin` is the harness for a team **without** a platform: Claude reads `metrics.yaml`
and compiles SQL itself, so every rule has to be in the skill text. This folder is the same
knowledge for a team **with** an agent platform that has a metric layer and a gateway:

| here | role |
|---|---|
| `metrics.yaml` | the same 12 metrics in the platform's sync format (`projects: demo:`). The platform compiles each spec into SQL and injects `tables.<t>.where` itself, so a filter cannot be skipped |
| `skills/clickhouse-mart` | mart rules through the gateway: structure from `clickhouse_schema`, numbers from `list_metrics` / `query_metric`, hand-written SQL only outside the catalog |
| `skills/gaming-analysis` | the casino table's adjustments and examples, for the hand-written case |
| `skills/basic-analytics` | presentation, plus regular delivery through a `metric_digest` schedule |

Read side by side with `../plugin`, the difference is the README's "What replaces the
platform" table in practice: the rule that the agent must remember there is enforced by the
server here.

The platform syncs these files from git (`metric_spec_sync` for `metrics.yaml`,
`skill_sync` for `skills/`), so a formula change is a reviewed PR in either form.
