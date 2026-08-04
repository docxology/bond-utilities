# data/ — agent guide

Versioned project **inputs** only. Generated CSVs/JSONs/PNGs belong under
`output/` (git-ignored), never here.

## `claim_ledger.yaml`

Evidence registry for manuscript claims sourced from code/config rather than
`{{TOKEN}}` injection. Each row: `claim_id`, `kind`, `value`, `source`,
`source_tier`, `freshness`, optional `artifact_path`.

## Edit protocol

1. Edit rows only when config, code defaults, or source-backed facts change.
2. Keep values consistent with `manuscript/config.yaml` and `src/`.
3. Never commit generated artifacts under `data/`.

See [`README.md`](README.md).
