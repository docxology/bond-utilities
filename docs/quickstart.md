# Quickstart — bond-utilities

A 5-minute first run.

## 1. Install

From inside this package directory:

```bash
uv sync --extra dev
```

## 2. Run the tests

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

Expect ≥90% line+branch coverage on `src/` (currently 100%), 0 failures.

## 3. Generate codenames (any scheme)

```bash
uv run python scripts/generate_codenames.py --count 6 --seed 20260804
uv run python scripts/generate_codenames.py --count 6 --seed 20260804 --scheme alliterative
```

## 4. Run cryptanalysis on a message

```bash
uv run python scripts/cryptanalyze.py "THEQUICKBROWNFOX"
uv run python scripts/cryptanalyze.py --vigenere-length 5 "SOMEVIGENERECIPHERTEXT"
```

## 5. Persist (and verify) a mission record

```bash
uv run python scripts/record_mission.py \
  --mission-id M-001 --payload '{"target":"grid"}' --verify --out output/data/missions/M-001.json
```

## 6. Hydrate the manuscript

```bash
uv run python scripts/z_generate_manuscript_variables.py
# writes output/data/manuscript_variables.json + both figures
```

## Try the library

```python
from bond_utilities import caesar_encrypt, caesar_break, nato_codename, MissionSchedule
print(caesar_encrypt("Q-BRANCH", 3))
print(caesar_break(caesar_encrypt("THEQUICKBROWNFOX", 7)))   # (7, 'THEQUICKBROWNFOX')
print(nato_codename("QB7"))                                   # 'QUEBEC-BRAVO-7'
```
