#!/usr/bin/env python3
"""Morning digest: a fresh harness chat writes it, a file keeps it, Slack gets it if set.

    python3 demo/digest.py             # write out/digest-<date>.md, post if configured
    python3 demo/digest.py --no-post   # file only

Where it goes is configuration, not a parameter: the Slack incoming webhook comes from
SLACK_WEBHOOK_URL in the environment of whoever runs the digest. A caller of this script
cannot point it at another channel.

Without a platform the schedule lives on this laptop (cron or a Claude Desktop scheduled
task): laptop asleep, no digest. That gap is the bridge to the platform part.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import time
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ask  # noqa: E402  (same folder; runs a fresh harness chat)

OUT = ask.HARNESS / "out"
MARKER = "## Answer"


def _answer(lines: list[str]) -> str:
    """The final answer only: everything after the answer marker, minus the cost line."""
    joined = "\n".join(lines)
    if MARKER not in joined:
        return ""
    tail = joined.split(MARKER, 1)[1].strip()
    return "\n".join(line for line in tail.splitlines() if not line.startswith("_")).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--no-post", action="store_true", help="do not post to Slack")
    args = parser.parse_args()

    _, prompt = ask._question("digest")
    text = _answer(ask.run(prompt, bare=False, timeout=300))
    if not text:
        print("No digest: the chat gave no answer, nothing was posted.")
        return 1

    OUT.mkdir(exist_ok=True)
    path = OUT / f"digest-{time.strftime('%Y-%m-%d')}.md"
    path.write_text(text + "\n", encoding="utf-8")
    print(f"\nFile: {path.relative_to(ask.HARNESS)}")

    hook = os.environ.get("SLACK_WEBHOOK_URL")
    if args.no_post or not hook:
        print("Not posted to Slack: " + ("--no-post." if args.no_post
                                         else "SLACK_WEBHOOK_URL is not set."))
        return 0
    body = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(hook, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        print(f"Slack: HTTP {resp.status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
