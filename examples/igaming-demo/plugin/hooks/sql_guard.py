#!/usr/bin/env python3
"""PreToolUse guard for the ClickHouse MCP server: read-only SQL, one statement, bounded.

Claude Code pipes the hook JSON to stdin. The guard answers with a permission decision:
  - deny  a statement that is not a read (INSERT, ALTER, DROP, GRANT, SYSTEM, ...);
  - deny  more than one statement in one call;
  - deny  `SELECT *` without LIMIT (a whole table into the chat is a bug, not an answer).
Anything else passes silently. The database role is the real boundary (SELECT only);
this guard is the second layer that refuses before the query leaves the laptop and says
why, so the model can fix the query instead of guessing.

Fail-closed on its own path only: if the input cannot be read, a ClickHouse tool call is
refused; the guard is never registered for other tools.
"""

from __future__ import annotations

import json
import re
import sys

READ_STARTS = ("SELECT", "WITH", "SHOW", "DESCRIBE", "DESC", "EXPLAIN", "EXISTS")
WRITE_WORDS = (
    "INSERT", "ALTER", "DROP", "CREATE", "TRUNCATE", "DELETE", "UPDATE", "RENAME",
    "GRANT", "REVOKE", "OPTIMIZE", "SYSTEM", "KILL", "ATTACH", "DETACH", "EXCHANGE",
    "UNDROP", "SET", "USE",
)
_COMMENTS = re.compile(r"--[^\n]*|/\*.*?\*/", re.S)
_QUOTED = re.compile(r"'(?:[^'\\]|\\.)*'|`[^`]*`|\"[^\"]*\"", re.S)


def _decide(decision: str, reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))


def check(sql: str) -> str | None:
    """Return a refusal reason, or None when the statement may run."""
    bare = _QUOTED.sub("''", _COMMENTS.sub(" ", sql)).strip().rstrip(";").strip()
    if not bare:
        return "Empty query."
    if ";" in bare:
        return "One call, one statement. Split it into separate calls."
    upper = bare.upper()
    if not upper.startswith(READ_STARTS):
        return "The harness is read-only: SELECT / WITH / SHOW / DESCRIBE / EXPLAIN only."
    hit = next((w for w in WRITE_WORDS if re.search(rf"\b{w}\b", upper)), None)
    if hit:
        return f"The query contains {hit}: the harness is read-only. Data changes go through the database owner."
    if re.search(r"\bSELECT\s+\*", upper) and not re.search(r"\bLIMIT\s+\d+", upper):
        return "SELECT * without LIMIT pulls the whole table into the chat. Add LIMIT or list the fields."
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        tool_input = payload.get("tool_input") or {}
        sql = tool_input.get("query") or tool_input.get("sql")
    except (ValueError, AttributeError):
        _decide("deny", "sql_guard: could not read the call, so it is refused.")
        return 0
    if sql is None:  # list_databases / list_tables: nothing to check
        return 0
    reason = check(str(sql))
    if reason:
        _decide("deny", reason)
    return 0


if __name__ == "__main__":
    sys.exit(main())
