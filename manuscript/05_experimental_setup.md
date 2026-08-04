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
| Cipher primitives | {{CIPHER_COUNT}} |
| Word-list capacity | {{WORDLIST_SIZE}} |
| Generation timestamp | {{GENERATION_TIMESTAMP}} |

## Software environment

The package requires Python ≥ 3.10 and depends only on `numpy`,
`matplotlib`, and `pyyaml`. Tests use `pytest` and `pytest-cov`; no mock
framework is used anywhere.
