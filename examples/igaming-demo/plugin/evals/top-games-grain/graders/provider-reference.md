---
type: llm
focus: last_message
weight: 2
---

PASS if the SQL returns one row per game and shows the provider as a reference column (for
example `groupUniqArray(game_provider)`), and the answer says the provider field
has aliases, so a game can list several provider values.

FAIL if the SQL groups by game and provider together, or the answer presents provider values
as exact without mentioning the aliasing.
