# bond-utilities TODO

Forward-only backlog for the bond-utilities package (codename **Q-BRANCH**),
Layer 0 of the BOND suite.

## Current status (phase 4 — deep improvement)

- **Ciphers** extended to 9 primitives (added Atbash, Beaufort, rail-fence,
  Playfair, columnar) + **8 cryptanalysis helpers** (letter frequency,
  normalized frequency, index of coincidence, English chi-squared,
  Caesar shift scores/break, Kasiski examination, Vigenère break).
- **Codenames** gained 4 new deterministic schemes (alliterative, NATO,
  numeric, token) via `codenames_by_scheme` and
  `generate_codenames(..., scheme=...)` (default unchanged).
- **Clock** added `windows_overlap`, `merge_windows`, `parse_duration`,
  `schedule_status`, and the `MissionSchedule` dataclass.
- **Randomness** added `seeded_bytes/int/float/choice/choices/shuffle/sample`;
  `ciphers.generate_otp_key` now delegates to `seeded_bytes` (byte-identical).
- **Mission I/O** added `verify_provenance`, `load_records`,
  `record_summary`, `append_outcome` (provenance preserved on append).
- **reporting** added `schedule_table` / `print_schedule_table`; **figures**
  added `plot_frequency_analysis` (second manuscript figure).
- **Tests**: 316 passed, 0 skipped, 0 failed; **100%** line+branch coverage
  on `src/` (gate ≥90%), zero mocks (pytest.MonkeyPatch only, no mock
  framework).
- **ruff + mypy**: clean on `src/` and `scripts/`.
- **Manuscript** updated: new sections/tokens (`CIPHER_NAMES_CSV`,
  `CODENAME_SCHEMES`, `CRYPTANALYSIS_HELPERS`, `NATO_EXAMPLE`,
  `RESULT_OVERLAP_HOURS`, `RESULT_SCHEME_SAMPLE`), `fig:freq` figure, and
  two new bib entries (Friedman 1922, Kasiski 1863).
- **Zero** `template[_]code_project`-style lineage strings in the tree (the
  grep command in docs is bracket-split so it cannot trip its own gate).

## Verification

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/
uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/
```

## Integration point (bond-api)

`src/bond_utilities/mission_io.py::record_provenance_outcome` remains the
persistence helper bond-api outcomes call. Phase 4 adds
`verify_provenance` (recompute input hash/seed/version), `append_outcome`
(merge results without disturbing provenance), `load_records` (directory
batch load), and `record_summary`. `scripts/record_mission.py` is the thin
CLI demonstrating the contract (with `--verify`).

## Open items

- [ ] Wire the manuscript render pipeline (PDF/output/manuscript) once the
      suite chooses a renderer; currently only tokens + both figures are
      produced.
- [ ] `vigenere_break` recovers keys reliably on letter-rich ciphertext;
      document a minimum column-sample guideline (kept in
      `07_scope_and_related_work.md`).
- [ ] If the word lists grow beyond 12×12, consider a
      `generate_codenames(..., allow_repeats=True)` knob (default stays
      unique).
- [ ] Keep live test count / coverage out of committed prose; the numbers
      above are snapshots for this commit only.

## Guardrails honored

Path-scoped, local-only commits · no mock framework · ≥90% coverage · all
existing public APIs and CLI contracts kept intact · deterministic seeding ·
thin orchestrators · computed manuscript variables · zero exemplar-lineage
strings.
