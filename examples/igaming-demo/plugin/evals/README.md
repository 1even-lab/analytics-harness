# Evals for the demo plugin

Same two levels as the template ([plugins/company-data/evals/README.md](../../../../plugins/company-data/evals/README.md)),
aimed at the traps of the demo data.

| case | catches |
|---|---|
| `mandatory-filters` | casino GGR SQL without the project exclusion, the window or the breakdown |
| `top-games-grain` | a game top grouped by the provider field, which is not 1:1 with the game |
| `non-additive` | weekly active players as a sum of daily values |
| `read-only-refusal` | agrees to delete rows |
| `golden/questions.yaml` | numbers against reference values of the deterministic demo data (needs the connector) |

Run from the plugin directory:
```bash
claude plugin eval . --threshold 0.9
```
