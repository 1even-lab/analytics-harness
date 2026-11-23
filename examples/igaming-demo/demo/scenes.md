# Demo scenes - "An analytics harness without a platform"

The host is the `demo-tour` skill (in `.claude/skills/` of this example). One scene per turn,
the next one on "next". Each scene has **Say** (talking points, retold in your own words),
**Do**, **Check** and **If it fails**. The whole demo takes 25-30 minutes.

Start the host from this folder with the plugin loaded, so it can run the reference queries:
`claude --plugin-dir plugin`.

---

## 1. What a harness is (3 min)

**Say.** Everyone has the same model. What differs is around it: what it knows about the
data, what it can reach, what it may not do, and how that is checked. That is the harness:
plain files in git that you can read, review and install. Here it is the repository's
`company-data` template, filled in for one warehouse.

**Do.** Show `plugin/`: `.claude-plugin/plugin.json`, `.mcp.json`, `hooks/`, and the skills
`data-router`, `metrics-catalog` (with `references/metrics.yaml`), `warehouse-mart`,
`gaming-activity-analysis`, `basic-analytics`, `dashboard`. Then `sql/`.

**Check.** The room sees the layers of `docs/DESIGN.md`: access, meaning, formulas,
routing, table pitfalls, presentation.

## 2. One owner per fact (4 min)

**Say.** Each kind of knowledge lives in one place. A field's meaning - in the warehouse
`COMMENT`. A formula - in `metrics.yaml`. A table's pitfalls - in its domain skill. A
skill that needs a formula points to the catalog instead of restating it.

**Do.** Open `metrics.yaml`: `tables.demo.gaming_activity.where` and the `ggr_games`
expression. Then `gaming-activity-analysis` - "Mandatory adjustments": the project with
real-money columns only.

**Check.** The room understands that `sum(casino_ggr_usd)` silently drops a whole brand,
and that the fix is written once.

## 3. Access is configuration (3 min)

**Say.** `.mcp.json` holds no host and no password, only environment variables. What the
agent may read is decided by the database: the role grants `SELECT` on `demo.*` and nothing
else. The skill text only explains what to say at the boundary.

**Do.** Show `plugin/.mcp.json` and `sql/03_access.sql` (the grant is on a role, the user
gets the role).

## 4. The hook at work (2 min)

**Say.** The hook is a second layer: it refuses before a query leaves the laptop and tells
the model why, so the model rewrites the query instead of guessing.

**Do.** Run in the terminal:
```bash
echo '{"tool_input":{"query":"DROP TABLE demo.gaming_activity"}}' | python3 plugin/hooks/sql_guard.py
echo '{"tool_input":{"query":"SELECT * FROM demo.gaming_activity"}}' | python3 plugin/hooks/sql_guard.py
echo '{"tool_input":{"query":"SELECT count() FROM demo.gaming_activity"}}' | python3 plugin/hooks/sql_guard.py
```
**Check.** The first two are `deny` with a reason, the third is silent (allowed).

## 5. A fresh chat: a question with traps (5 min)

**Say.** This chat will not ask the question - it has already read the skills aloud. A new,
clean chat in an empty folder gets the plugin and nothing else.

**Do.** `python3 demo/ask.py q1` - the room sees the SQL the new chat writes, and the answer.

**Check.** The SQL substitutes the real-money GGR for one project and excludes another;
the answer names NovaSpin's missing days. The host runs `demo/checks/q1.sql` and
`demo/checks/q1_daily.sql`: the TOTAL matches the daily table and the answer.

**If it fails.** `python3 demo/ask.py q1 --replay` - and say it is a recording.

## 6. The same question without the harness (4 min)

**Say.** Same model, same database, same read permissions. Only the plugin is gone.

**Do.** `python3 demo/ask.py q1 --bare`. Then the host runs `demo/checks/q1_naive.sql` -
the query people usually write.

**Check.** Without the harness one brand is missing or zero and an excluded project is
counted in. The gap between the totals, in percent, is the key number of the demo. Say it.

**If it fails.** `--replay` with `--bare`.

## 7. Investigation, top-N and refusal (4 min)

**Do.** `python3 demo/ask.py q3` - NovaSpin's drop: expect three days with no rows, called
missing data, not "players left". Then `q2` - top games: one row per game, providers as a
reference column. Then `q4` - a request to delete data.

**Check.** q3: the days are named, no zeros filled in. q2: the most popular game is one row,
not split by provider aliases. q4: a refusal; if the chat tried `ALTER ... DELETE` anyway, the
output shows the hook's `✗ refused`.

## 8. Evals: how a harness stays correct (3 min)

**Say.** Without a platform the agent compiles SQL from text, so any edit to a skill can
silently break a number. Behavioural cases run without data on every PR; the golden set
runs with the connector before a release.

**Do.** Show `plugin/evals/mandatory-filters/case.yaml` and `plugin/evals/golden/questions.yaml`
(reference numbers that every load of this dataset reproduces).

## 9. The digest, and where the harness ends (3 min)

**Say.** A scheduled report is the same fresh chat, only a timer asks the question. Where it
goes is configuration (`SLACK_WEBHOOK_URL` in the environment), not a parameter.

**Do.** `python3 demo/digest.py --no-post` - the file lands in `out/`.

**Say (the bridge).** The digest lives on a laptop: lid closed, no digest. The catalog is
text the model compiles itself and may skip a filter. Permissions are personal, not the role
of a scenario. These are the three things an agent platform takes over - the README's "What
replaces the platform" table read backwards.

**Cleanup.** Delete `out/` and any schedule created during the demo.
