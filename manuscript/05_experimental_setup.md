# Experimental setup

## Mission parameters

All values are read from `manuscript/config.yaml` by
`src/bond_utilities/manuscript_variables.py::generate_variables()`; scripts
never hardcode them.

| Parameter | Value |
| --- | --- |
| Package version | {{PACKAGE_VERSION}} |
| Mission codename | {{MISSION_CODENAME}} |
| Default seed | {{CONFIG_DEFAULT_SEED}} |
| Codename sample size | {{CONFIG_NUM_CODENAMES}} |
| Schedule start (UTC) | {{CONFIG_SCHEDULE_START}} |
| Schedule end (UTC) | {{CONFIG_SCHEDULE_END}} |
| Window duration | {{RESULT_WINDOW_HOURS}} hours |
| Overlap with secondary window | {{RESULT_OVERLAP_HOURS}} hours |
| Cipher primitives | {{CIPHER_COUNT}} |
| Cipher registry | {{CIPHER_NAMES_CSV}} |
| Codename schemes | {{CODENAME_SCHEME_COUNT}} ({{CODENAME_SCHEMES}}) |
| Cryptanalysis helpers | {{CRYPTANALYSIS_HELPERS}} |
| Seeded draw helpers | {{SEEDED_HELPER_COUNT}} ({{SEEDED_HELPERS_CSV}}) |
| Word-list grid | {{WORDLIST_SIZE}} |
| Word-list capacity (unique pairs) | {{WORDLIST_CAPACITY}} |
| Coverage gate | {{COVERAGE_GATE_PERCENT}}% line + branch on `src/` |
| Tolerated test failures | {{MAX_TEST_FAILURES}} |
| Manuscript date (config `paper.date`) | {{CONFIG_MANUSCRIPT_DATE}} |

## Software environment

The package requires Python ≥ 3.10 and depends only on `numpy`,
`matplotlib`, and `pyyaml`. Tests use `pytest` and `pytest-cov`; no mock
framework is used anywhere. All randomness is seeded; functions with a
wall-clock default take an explicit `now=/seed=` override in tests.
