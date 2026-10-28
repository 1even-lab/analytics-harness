---
type: llm
focus: last_message
weight: 2
---

PASS if the answer says that the budget is defined at the campaign-and-month level, so
a daily breakdown gives no correct number (the value repeats on every day), and offers a monthly
breakdown or a breakdown by campaign/channel.

FAIL if the answer builds a daily budget series, sums budget_usd across days, or divides the
monthly budget by the number of days without explicitly noting that this is outside the catalog.
