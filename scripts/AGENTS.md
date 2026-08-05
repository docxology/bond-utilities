# scripts/ — thin orchestration

BOND suite — bond-utilities. Scripts are thin orchestrators: they parse
args, call `src/bond_utilities`, and render output. No business logic here.

| Script | Purpose |
| --- | --- |
| `generate_codenames.py` | Print deterministic codenames (any scheme) via `reporting` |
| `record_mission.py` | Persist a provenance-outcome mission record; `--verify` re-verifies |
| `cryptanalyze.py` | Run frequency/IC/Kasiski/Caesar/Vigenère analysis on a message |
| `z_generate_manuscript_variables.py` | Hydrate `output/data/manuscript_variables.json` + render both figures (`z_` = runs last) |

Run any script from the package root:

```bash
uv run python scripts/generate_codenames.py --count 6 --seed 20260804
uv run python scripts/generate_codenames.py --count 6 --scheme alliterative
uv run python scripts/record_mission.py --mission-id M-001 --verify --out output/m.json
uv run python scripts/cryptanalyze.py "THEQUICKBROWNFOX"
uv run python scripts/z_generate_manuscript_variables.py
```
