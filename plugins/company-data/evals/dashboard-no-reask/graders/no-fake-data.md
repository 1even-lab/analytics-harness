---
type: llm
focus: last_message
weight: 3
---

PASS if the answer contains no invented metric values: either it says there is no data
access and offers SQL / a scaffold with placeholders, or the values are explicitly marked as
sample placeholders.

FAIL if the dashboard or the text contains plausible GGR or player numbers presented as real.
