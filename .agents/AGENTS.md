# .agents — AGENTS.md

Per-folder technical reference for the project-local agent scaffolding.

| Subdirectory | Purpose |
| --- | --- |
| [`skills/`](skills/AGENTS.md) | Project-local skills. Each ships `SKILL.md` with YAML frontmatter. |
| [`skills/bond-utilities/`](skills/bond-utilities/AGENTS.md) | Skill for building/maintaining this package. |

## When to update

- A new skill specific to this package or the BOND suite lands → add a folder
  under `skills/<name>/`.
