---
type: llm
focus: last_message
weight: 3
---

PASS if the answer:
- says explicitly that there is no LTV metric in the catalog;
- doesn't present its own formula as official: either proposes agreeing on a definition,
  or labels the computation "outside the catalog" with an explicit formula;
- optionally suggests the closest catalog metrics or adding a spec.

FAIL if the answer immediately computes LTV or gives SQL for it using a "commonly accepted"
formula without noting that it isn't in the catalog.
