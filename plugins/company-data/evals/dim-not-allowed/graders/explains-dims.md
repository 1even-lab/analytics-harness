---
type: llm
focus: last_message
weight: 2
---

PASS if the answer says that the GGR metric has no breakdown by acquisition channel
(it is not among the allowed dimensions) and offers the available breakdowns (date, country,
platform, game, provider) or adding the breakdown via a spec change.

FAIL if the answer silently builds a channel breakdown, joins another table to get the channel
without a caveat, or invents a column.
