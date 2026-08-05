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

The run prints the measured line+branch coverage of `src/` and fails below the
`fail_under` floor in `pyproject.toml`. Read the number from the run rather
than from any document.

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
from bond_utilities import caesar_encrypt, caesar_break, nato_codename

print(caesar_encrypt("Q-BRANCH", 3))                          # 'T-EUDQFK'

# caesar_break scores all 26 shifts by chi-squared fit against English letter
# frequencies, so it needs a letter-rich sample. A 35-letter pangram is enough:
print(caesar_break(caesar_encrypt("THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG", 7)))
# (7, 'THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG')

# A 16-letter sample is not enough — the statistic prefers a different shift,
# and the function returns that wrong answer rather than signalling low
# confidence. This is measured behaviour, not a hypothetical:
print(caesar_break(caesar_encrypt("THEQUICKBROWNFOX", 7)))
# (23, 'DROAESMULBYGXPYH')

print(nato_codename("QB7"))                                   # 'QUEBEC-BRAVO-7'
```

Every output quoted above is asserted against the live functions in
`tests/test_documented_examples.py`, which also checks that this file still
contains the exact strings — so a doc example cannot drift from the code.
