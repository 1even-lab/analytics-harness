"""Check metrics.yaml before merge: required fields, table references, dims and dedup."""

import sys
from pathlib import Path

import yaml

DEFAULT_PATH = Path("plugins/company-data/skills/metrics-catalog/references/metrics.yaml")
REQUIRED = ("title", "description", "table", "time_column", "unit", "expression", "dims", "owner")
UNITS = {"USD", "count", "users", "pct", "ratio"}


def validate(path: Path) -> list[str]:
    spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    tables = spec.get("tables") or {}
    errors: list[str] = []
    titles: dict[str, str] = {}

    for key, m in (spec.get("metrics") or {}).items():
        missing = [f for f in REQUIRED if f not in m]
        if missing:
            errors.append(f"{key}: missing fields {missing}")
            continue
        if m["table"] not in tables:
            errors.append(f"{key}: table {m['table']} is not in tables - shared filters won't apply")
        if m["unit"] not in UNITS:
            errors.append(f"{key}: unit {m['unit']!r} is not one of {sorted(UNITS)}")
        if not isinstance(m["dims"], dict):
            errors.append(f"{key}: dims must be a mapping alias → column")
        if not isinstance(m.get("where", []), list):
            errors.append(f"{key}: where must be a list of conditions")
        if m["title"] in titles:
            errors.append(f"{key}: title {m['title']!r} is already used by {titles[m['title']]}")
        titles[m["title"]] = key
        dedup = m.get("dedup")
        if dedup and not (dedup.get("by") and dedup.get("measure")):
            errors.append(f"{key}: dedup needs both by and measure")

    return errors


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    problems = validate(path)
    for p in problems:
        print(p)
    print("OK" if not problems else f"{len(problems)} errors")
    sys.exit(1 if problems else 0)
