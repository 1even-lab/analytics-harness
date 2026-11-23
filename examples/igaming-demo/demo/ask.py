#!/usr/bin/env python3
"""Ask one question in a FRESH Claude Code chat and show what it did.

    python3 demo/ask.py q1              # question q1 from demo/questions.json, with the harness
    python3 demo/ask.py q1 --bare       # same question, same database, no harness
    python3 demo/ask.py "any question"  # free text
    python3 demo/ask.py q1 --record     # also save demo/recordings/q1.md
    python3 demo/ask.py q1 --replay     # print the saved recording (fallback on stage)

Why a fresh chat in an empty temp folder: the presenter's chat has already read the skills
aloud, so its answer proves nothing. The new chat gets the harness plugin (`--plugin-dir`)
and nothing else: user settings, user plugins and user MCP servers are left out
(`--setting-sources local`, `--strict-mcp-config`), so a skill or a connector installed on
the presenter's machine cannot answer instead of the harness.

`--bare` gives the same database connection and the same read tools, and nothing else: no
plugin, so no skills, no metric specs and no hook. The difference between the two answers is
the harness.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import threading
import time

HARNESS = pathlib.Path(__file__).resolve().parents[1]
PLUGIN = HARNESS / "plugin"
DEMO = HARNESS / "demo"
RECORDINGS = DEMO / "recordings"
# The connector is loaded explicitly from the plugin's .mcp.json, so its tools are
# mcp__clickhouse__*; a server-level rule allows them all (they are all reads).
READ_TOOLS = ["mcp__clickhouse"]


def _question(arg: str) -> tuple[str, str]:
    questions = json.loads((DEMO / "questions.json").read_text(encoding="utf-8"))
    if arg in questions:
        return arg, questions[arg]
    return "custom", arg


def _workdir(bare: bool) -> pathlib.Path:
    # Empty on purpose: no CLAUDE.md, no project skills, no project settings.
    return pathlib.Path(tempfile.mkdtemp(prefix="igaming-demo-" + ("bare-" if bare else "")))


def _command(text: str, bare: bool) -> list[str]:
    cmd = [
        "claude", "-p", text,
        "--output-format", "stream-json", "--verbose",
        "--setting-sources", "local",
        "--mcp-config", str(PLUGIN / ".mcp.json"), "--strict-mcp-config",
        "--allowedTools", *READ_TOOLS,
        "--no-session-persistence",
    ]
    if bare:
        cmd += ["--disable-slash-commands"]
    else:
        cmd += ["--plugin-dir", str(PLUGIN)]
    return cmd


def _short(value: object, limit: int = 400) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    text = text.strip()
    return text if len(text) <= limit else text[:limit] + f" … [{len(text) - limit} more chars]"


def _tool_result_text(content: object) -> str:
    if isinstance(content, list):
        return "\n".join(c.get("text", "") for c in content if isinstance(c, dict))
    return str(content)


def run(text: str, bare: bool, timeout: int) -> list[str]:
    """Run the fresh chat, echo its steps live, return the transcript as markdown lines."""
    work = _workdir(bare)
    out: list[str] = []

    def emit(line: str = "") -> None:
        print(line, flush=True)
        out.append(line)

    proc = subprocess.Popen(_command(text, bare), cwd=work, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, encoding="utf-8")
    # A silent hang never yields a line, so the deadline is a timer, not a loop check.
    watchdog = threading.Timer(timeout, proc.kill)
    watchdog.start()
    try:
        assert proc.stdout is not None
        for raw in proc.stdout:
            try:
                event = json.loads(raw)
            except ValueError:
                continue
            kind = event.get("type")
            if kind == "assistant":
                for part in event.get("message", {}).get("content", []):
                    if part.get("type") == "tool_use":
                        name = part.get("name", "").replace("mcp__clickhouse__", "clickhouse.")
                        sql = (part.get("input") or {}).get("query")
                        if sql:
                            emit(f"→ {name}")
                            emit("```sql\n" + sql.strip() + "\n```")
                        else:
                            emit(f"→ {name} {_short(part.get('input'), 160)}")
            elif kind == "user":
                for part in event.get("message", {}).get("content", []):
                    if isinstance(part, dict) and part.get("type") == "tool_result":
                        mark = "✗ refused" if part.get("is_error") else "←"
                        emit(f"{mark} {_short(_tool_result_text(part.get('content')), 300)}")
            elif kind == "result":
                emit("\n## Answer\n")
                emit(event.get("result", "").strip())
                cost = event.get("total_cost_usd")
                emit(f"\n_{event.get('num_turns', '?')} turns, "
                     f"{event.get('duration_ms', 0) / 1000:.0f} s"
                     + (f", ${cost:.2f}" if cost is not None else "") + "_")
        proc.wait(timeout=10)
    finally:
        watchdog.cancel()
        if proc.poll() is None:
            proc.kill()
        shutil.rmtree(work, ignore_errors=True)
    if proc.returncode == -9:
        emit(f"\n⏱ The chat did not finish within {timeout} s and was stopped. Recording: --replay.")
    elif proc.returncode not in (0, None) and proc.stderr is not None:
        emit("\nLaunch error: " + _short(proc.stderr.read(), 600))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("question", help="id from demo/questions.json or the question text")
    parser.add_argument("--bare", action="store_true", help="no CLAUDE.md, skills or hooks")
    parser.add_argument("--record", action="store_true", help="save to demo/recordings/")
    parser.add_argument("--replay", action="store_true", help="print the saved recording")
    parser.add_argument("--timeout", type=int, default=240, help="seconds before giving up")
    args = parser.parse_args()

    qid, text = _question(args.question)
    rec = RECORDINGS / f"{qid}{'-bare' if args.bare else ''}.md"
    if args.replay:
        if not rec.exists():
            print(f"No recording {rec.name}: run with --record first.")
            return 1
        print("▶ RECORDING of an earlier run, not a live answer\n")
        print(rec.read_text(encoding="utf-8"))
        return 0

    header = f"# {'Without the harness' if args.bare else 'With the harness'}: {text}"
    print(header + "\n", flush=True)
    lines = run(text, args.bare, args.timeout)
    if args.record:
        RECORDINGS.mkdir(exist_ok=True)
        stamp = time.strftime("%Y-%m-%d %H:%M")
        rec.write_text("\n".join([header, f"_recorded {stamp}_", "", *lines]) + "\n",
                       encoding="utf-8")
        print(f"\n(saved to {rec.relative_to(HARNESS)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
