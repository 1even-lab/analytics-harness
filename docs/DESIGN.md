# Why the harness is built this way

The [README](../README.md) explains what is in this repository and how to adopt it. This
document explains the reasoning: which problems the harness answers, the two principles
behind its layout, and which layer owns which kind of knowledge.

## What a harness is

An analytics harness is the set of skills, metric definitions, query examples and tests
that tells an AI agent how to work with a company's data. It lives in git, changes through
review, and is installed into the tools people already use.

The warehouse says what the data is. The harness says how to use it to answer a question.

## The problems it answers

These show up in any team that points AI agents at a warehouse. None of them depends on a
particular stack.

| Problem | What it looks like |
|---|---|
| Rules drift apart | The same rules are copied into each tool's config and into personal setups. The copies diverge and nobody notices. |
| Context fills up | Schemas and formulas are pasted into prompts. Every request pays for them, and the agent pays less attention to the question. |
| Policy lives in a prompt | "Read-only, production is off limits" is written as an instruction. An instruction is a request; it guarantees nothing. |
| Each agent has its own formula | Without a shared dictionary, every agent and every analyst derives a metric their own way, and the numbers do not match. |
| Knowledge stays with people | Corrections and data quirks sit in chat histories and in the heads of senior analysts. |
| Every start is a cold start | A new tool or a new colleague begins from nothing, with a setup nobody reviewed. |

## Two principles

### Every fact has one owner

Each kind of knowledge is written down in exactly one place. Everything else points to that
place and does not repeat it.

A field's meaning is written in the warehouse `COMMENT`. A metric's formula is written in
`metrics.yaml`. A table's pitfalls are written in that table's skill. When a skill needs a
formula, it tells the agent to open the catalogue; it does not restate the formula.

This removes four of the six problems at once. Rules cannot drift when there is one copy.
Context stays small because the agent loads only the layer it needs. Metrics agree because
there is one definition. Knowledge has a place to go when someone finds a quirk.

### Access is enforced by configuration; the prompt only explains

What the agent may read is decided by database grants and by the connector's read-only
user. The skill text does not grant or restrict access. It tells the agent what to say when
it reaches the boundary, for example when the data it needs is not in `mart`.

The same applies to exclusions that must always hold. A filter that no query may skip
belongs in the warehouse as a row policy or a view, where it cannot be forgotten.

## Which layer owns what

Before adding anything to the harness, decide which layer owns it.

| Layer | Owns | Does not contain | When the agent reads it |
|---|---|---|---|
| Database grants and the connector's read-only user | Access: which schemas are visible, that writes are impossible | Anything else | Never. It applies to every query from outside the agent |
| `COMMENT`s on warehouse tables and columns | What a table and a field mean: units, currency, grain, traps | Metric formulas, procedures | On demand, through the connector, for the table in play |
| `metrics-catalog/references/metrics.yaml` | Metric definitions: expression, table, time column, allowed breakdowns, filters, `dedup`, `caveat`, owner. Filters shared by a whole table sit once under `tables.<t>.where` | Field descriptions; explanations longer than two sentences | When the question names a metric |
| `data-router` | Routing: what is connected and which skills apply | Formulas, schemas, SQL rules | On every data question |
| `warehouse-mart` | Rules for hand-written SQL: which layer to read, how to find a table, what a safe query looks like | Metric formulas, table schemas | When a metric is not in the catalogue or the slice is ad hoc |
| A domain skill, one per table with pitfalls | The mandatory adjustments for that table and example queries with them applied | General SQL rules, other tables | When the question touches that table |
| `basic-analytics`, `dashboard`, `bi-reporting` | How the answer is presented and delivered | Where the numbers come from | When the answer is being shaped |
| `references/` inside a skill | Long material and material that changes often: specs, SQL examples, datasource ids, the HTML scaffold | Rules that must always be in context | Only when the skill links to it |
| `evals/` | What correct behaviour looks like: behavioural cases and reference numbers signed off by metric owners | Rules for the agent | Never. CI and the release check run it |

Two consequences follow from the table.

A skill describes a procedure and stays short. If a `SKILL.md` starts to hold a table schema
or a formula, that content has an owner elsewhere and should move there.

A specific skill owns the "what": sources, metrics, corrections. A general skill owns the
"how" and defers to the specific one in its own text. `warehouse-mart` says so directly: a
metric in the catalogue is computed by the catalogue, not by a formula written on the spot.

## Where to put a new piece of knowledge

| You learned that | Put it in |
|---|---|
| a field is in cents, or a table has one row per player per day | the `COMMENT` on that field or table |
| a metric needs another filter, or must not be split by some dimension | `metrics.yaml`: `where`, `dims` or `caveat` |
| a filter applies to every metric of a table | `tables.<t>.where`, or better, a row policy or a view in the warehouse |
| a table repeats a value across rows, or has another trap | that table's domain skill, plus the metric's `caveat` |
| answers should state the period, or a chart needs another default | `basic-analytics` or `dashboard` |
| the agent must not see some data | grants or a row policy. Skill text is the wrong place |
| the agent gave a wrong answer | a new case in `evals/`, in the same PR as the fix |

## What the harness cannot guarantee

The agent applies these rules itself, from the text of the skills. No server stands between
the agent and the warehouse to add a missing filter or reject a query. The README section
"What replaces the platform" lists each rule a platform would enforce and what stands in
for it here.

Three things reduce the risk. Shared filters are written once per table, so there are fewer
places to forget one. Filters that must never be skipped move into the warehouse. Evals run
on every change and catch a skill edit that breaks a computation.

The risk does not go away. A team that needs the rules enforced, needs scheduled delivery,
or needs each person's own permissions applied to each query has outgrown a harness and
needs a platform under it.

## Scope

This template targets Claude: the skills are packaged as a plugin and installed from a
marketplace into claude.ai, Claude Desktop and Claude Code. The two principles and the
ownership table do not depend on the tool. Syncing the same skills into other agents is
possible, but this repository does not include that step.

## Where it sits in the CAPTURE Framework

The harness is the outcome of the Unify stage of the
[CAPTURE Framework](https://github.com/1even-lab/capture-framework). By that stage a team
has accumulated table descriptions, metric definitions, corrections and skills written by
different analysts. Unify sorts that material into layers, moves it into git and puts it
under review and tests. This repository is a worked example of the result.

## Licence and author

This document is part of the repository and is covered by its MIT licence ([LICENSE](../LICENSE)). Written by Max Ivanov, 1even.lab.
