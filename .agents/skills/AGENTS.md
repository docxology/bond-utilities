# .agents/skills — AGENTS.md

Per-folder technical reference for the project-local skill catalog. One folder
per skill; each ships `AGENTS.md`, `README.md`, `SKILL.md`.

| Skill | Purpose |
| --- | --- |
| [`bond-utilities/`](bond-utilities/AGENTS.md) | BOND suite foundation (Q-BRANCH): build/maintain the shared package. |

## Skill contract

Every skill folder must ship:

- `SKILL.md` — YAML frontmatter (`name`, `description`, `version`, `tags`,
  …) + body with **when to use**, **quick reference**, **pitfalls**,
  **cross-refs**.
- `AGENTS.md` — short technical reference for the folder.
- `README.md` — purpose + pointer.
