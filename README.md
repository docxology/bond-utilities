# bond-utilities

**Q-BRANCH** is the Layer 0 Python library for the BOND suite. It supplies
classical ciphers for demonstrations, deterministic codenames, UTC schedule
math, seeded randomness, provenance records, and plain-text reports for
fictional mission examples.

## Install and verify

The distribution is `bond-utilities`; import it as `bond_utilities`.
From this checkout with [uv](https://docs.astral.sh/uv/) installed:

```sh
uv sync --locked --extra dev --python 3.14
uv run --no-sync --python 3.14 pytest --no-cov tests/test_clock.py
```

This check exercises the UTC scheduling helpers. See the
[test guide](docs/tests.md) for the full package gate.

- [Documentation index](docs/README.md)
- [Quickstart and CLI commands](docs/quickstart.md)
- [Library and worked examples](docs/library.md)
- [Manuscript source](docs/manuscript/README.md)
- [Render and validate the manuscript](docs/rendering.md)

## License

[MIT](LICENSE).
