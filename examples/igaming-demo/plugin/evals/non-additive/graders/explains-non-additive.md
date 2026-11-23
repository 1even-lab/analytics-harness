---
type: llm
focus: last_message
weight: 3
---

PASS if the answer explains that weekly unique players can't be obtained by summing
daily values (one player is counted on several days) and proposes computing the metric per spec on
a weekly window. Stating bounds is fine: no less than the daily maximum (1500) and no more than the sum.

FAIL if the answer gives the sum or the average of daily values as the weekly active players.
