# `src/bond_utilities` — Q-BRANCH primitives

The importable foundation of the BOND suite. See
[`AGENTS.md`](AGENTS.md) for the module map and rules.

```python
from bond_utilities import (
    caesar_encrypt,          # ciphers
    generate_codenames,      # codenames
    make_rng,                # randomness
    record_provenance_outcome,  # mission_io
    format_table,            # reporting
)
```

Run the test gate from the package root:

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```
