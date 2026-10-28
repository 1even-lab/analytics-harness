# Plugin evals

Without a platform, the agent compiles SQL itself from the skill text, so any change to a skill
or spec can silently break a computation. Evals catch this before merge.

Two levels:

| what | where | data | when to run |
|---|---|---|---|
| **behavioral cases** | `evals/<case>/` | not needed | on every PR to the marketplace |
| **golden set** | `evals/golden/questions.yaml` | real connector | before releasing a version and after table changes |

## Behavioral cases

Format of `claude plugin eval`: `case.yaml` (prompt, limits, graders) and `graders/*.md`
(rubrics for the LLM grader). There is no warehouse connector in the run, so the agent works in
"methodology only" mode (`data-router`, section C): it returns SQL in the answer, and regexes
check that SQL.

| case | catches |
|---|---|
| `no-connector-no-numbers` | states "rough" numbers with no data |
| `mandatory-filters` | a mandatory filter, window or breakdown is missing from the SQL |
| `dim-not-allowed` | substitutes a breakdown that isn't in `dims` |
| `unknown-metric` | invents a formula for a metric outside the catalog |
| `non-additive` | sums unique players across days |
| `dedup-grain` | slices a monthly measure by day |
| `dashboard-no-reask` | asks for the format when told "dashboard"; draws fake numbers |
| `read-only-refusal` | agrees to modify data |
| `off-topic-no-trigger` | data skills fire on a question that isn't about data |

Run from the plugin directory (Claude Code v2.1.269+; "early access" message = run `claude update`):
```bash
claude plugin eval . --threshold 0.9
```
Each case runs 3 times with the plugin and 3 times without it (baseline); the report shows
`WITH`, `W/OUT` and `Δ` - how much the plugin itself contributes. Iterating on one case cheaply:
`--case <name> --runs 1 --ablation none`.

How graders count:
- regex / `tool_used` are free; `llm` graders call a judge model (small fast model by default,
  `--judge-model sonnet` for nuanced rubrics) and pass on 2 of 3 votes.
- `tool_used: Skill` graders ("the skill fired") are **indicators, not scored** in a two-arm run -
  they can never pass without the plugin. The score comes from the regex and `llm` graders.
- A "must not fire" check needs `min: 0`, `max: 0` and `arm: both` (see `off-topic-no-trigger`).

CI:
```bash
claude plugin eval plugins/company-data --trust-plugin --json results.json --no-publish \
  --threshold 0.8 --model <pinned-model> --judge-model <pinned-judge> --max-cost-usd 20
```
Pin both models so a model rollout isn't mistaken for a plugin regression. Exit codes: `0` all
cases at or above threshold, `1` a case below threshold or a load error, `2` partial run (cost
ceiling or rejected credentials). Needs `ANTHROPIC_API_KEY` (or other credentials) on the runner.
Every run and every judge call is a real model call billed to your account.

**Adding a case.** Every defect found in an answer is a candidate case: the prompt verbatim
from the complaint, a grader for that specific mistake. Deterministic checks (regex on SQL,
`tool_used`) are preferable to LLM rubrics: they are cheaper and don't drift.

## Cases with data (MCP mocks)

If the warehouse connector is declared in the plugin (`.mcp.json`), its responses can be
replaced by a mock to test behavior on data - window freshness, reaction to a SQL error:

```
evals/mocks/<server>/<tool>.md          # mock for all cases
evals/<case>/mocks/<server>/<tool>.md   # mock for one case only
```
```markdown
---
type: agent
---
You are the warehouse. For max(event_date) from mart.player_daily return 2026-09-20.
For other SELECTs return 3-5 plausible rows as JSON. For anything other than SELECT return an access error.
```
The SQL the agent sent is checked by a grader with `target: mock_calls`.
`<server>` must match the server name in the plugin config; if users connect the warehouse
separately (not from the plugin), this level is unavailable - use the golden set.

## Golden set

Questions with a reference answer signed off by the metric owner. Run with a real connector:
ask the agent the question, compare the number with `expected` and the SQL with `sql_must`.
The reference is taken for a **closed** period, otherwise it drifts along with the data.
A discrepancy is a regression: in a skill, a spec or the table's data.

Run results (`evals/results/`) are not committed to git.
