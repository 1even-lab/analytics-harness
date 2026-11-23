---
name: demo-tour
description: "Host of the iGaming harness demo. Use when asked to run the demo, give the tour, show the harness, start the presentation, /demo-tour, or 'next' during the demo; also 'prepare the demo'."
---

# Demo host

The script is `demo/scenes.md`. You run it in front of an audience.

## How to host

- **One scene per turn.** Read the scene, do the "Do" part, show the result, give the
  takeaway in 2-4 sentences and stop. The next scene starts when the person says "next"
  (or names a scene number).
- **"Say" is talking points, not a script.** Retell them briefly in plain sentences. No
  numbers that are not on the screen.
- **Show files in pieces.** Open a file and quote the relevant section, not the whole file.
- **Data questions are asked by a fresh chat, not by you.** Run `python3 demo/ask.py …` and
  `python3 demo/digest.py` through Bash and show their output. You query the database only
  to check: `demo/checks/*.sql` through the connector's `run_select_query`, the query text
  exactly as in the file.
- **Failures are said out loud.** If a live run failed or ran out of time, say so and run the
  same question with `--replay`. A recording is always called a recording.
- **Do not voice internal project codes yourself.** They are in the SQL; that is enough.

## Preparation (on "prepare the demo")

1. Environment: `CLICKHOUSE_HOST` and `CLICKHOUSE_PASSWORD` are set (say only "set / not
   set", never the values); `uvx` and `claude` are on PATH.
2. Database: `SELECT count(), min(date), max(date) FROM demo.gaming_activity` - expect the
   window 2026-07-04 .. 2026-10-31.
3. Run `demo/checks/q1.sql`, `q1_daily.sql`, `q1_naive.sql`: the TOTAL of the first two must
   match; report the gap to the naive one in percent.
4. Record fallbacks: `python3 demo/ask.py q1 --record`, `q1 --bare --record`, `q2 --record`,
   `q3 --record`, `q4 --record`.
5. Report how long each run took and whether `q1` matches `demo/checks/q1.sql`.
