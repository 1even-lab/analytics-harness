# <BI> - tool specifics

Copy this file for each BI tool (`<bi-name>.md`) and link it from SKILL.md.
This is what changes more often than the rules: datasource names, ids, data windows, MCP tools.

## Connection
- MCP connector: `<bi-mcp>`; permissions: <read | read and write cards>.
- Database for new cards: `<warehouse connection name>`. Legacy connections
  (`<name>`) - read only; no new cards on them.

## Approved datasources

| scenario | datasource | id | table |
|---|---|---|---|
| player KPIs | `<player_daily>` | `<id>` | `mart.player_daily` |
| casino | `<casino_rounds>` | `<id>` | `mart.casino_rounds` |

## Windows and limitations
- `<player_daily>` is truncated to the last <N> months - go to the warehouse for older history.
- <other specifics: totals smeared across rows, empty fields on some rows>.

## MCP tools
| task | tool |
|---|---|
| list datasources | `<list-datasources>` filtered by tag |
| metadata | `<get-metadata>` |
| query | `<query-datasource>` |
| search cards | `<search>` |
| create / update a card | `<create>` / `<update>` |
