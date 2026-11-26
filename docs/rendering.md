# Render and validate the manuscript

The maintained source is in [`docs/manuscript/`](manuscript/README.md).
Its [configuration](manuscript/config.yaml) supplies publication metadata,
the fictional mission sample, and the validation thresholds. Its preamble
and bibliography travel with the source.

Use Git, uv, Python 3.14, Pandoc 3.14, pandoc-crossref 0.3.26 built against
Pandoc 3.14, and XeLaTeX with Beamer and BibTeX. The pinned template's
`scripts/shell/setup-system-deps.sh --check` can check its TeX dependencies.

## Register the checkout and generate inputs

From the bond-utilities checkout, clone the shared renderer and register a
physical working-project checkout. Stage 03 runs the project's generator
inside this directory.

```bash
project_source="$(pwd -P)"
git clone https://github.com/docxology/template.git ../template-renderer
renderer_root="$(cd ../template-renderer && pwd -P)"
git -C "$renderer_root" checkout --detach 87704feae0a4490ef7dad9c931d268e8c30273c2
(cd "$renderer_root" && uv sync --locked --no-dev)
mkdir -p "$renderer_root/projects/working"
git clone "$project_source" "$renderer_root/projects/working/bond-utilities"
cd "$renderer_root/projects/working/bond-utilities"
git checkout --detach
project_root="$(pwd -P)"
uv sync --locked --extra dev --python 3.14
uv run --no-sync --python 3.14 python scripts/z_generate_manuscript_variables.py
```

The generator writes the reported values and both PNGs under `output/`.
The shared renderer reads an intermediate manuscript tree with those values
resolved. Generate the intermediate tree from the pinned template root and
then run Stages 03 and 04.

```bash
cd "$renderer_root"
uv run --no-sync python - "$project_root" <<'PY'
import json
import sys
from pathlib import Path

from infrastructure.rendering.manuscript_injection import write_resolved_manuscript_tree

project = Path(sys.argv[1])
variables = json.loads((project / "output/data/manuscript_variables.json").read_text())
write_resolved_manuscript_tree(project, variables)
PY
uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/bond-utilities
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/bond-utilities
```

If you change source or configuration, rerun the project generator and the
intermediate manuscript step before rendering. The working checkout receives
the combined PDF at `output/pdf/bond-utilities_combined.pdf`, combined HTML
at `output/web/index.html`, and section decks in `output/slides/`. Check the
combined editions for the package results, both generated figures, and
resolved bibliography entries. Stage 04 writes `output/reports/validation_report.json`
and `output/reports/rendered_provenance.json`.

See the pinned [project integration guide](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/projects/README.md#L208-L223),
[manuscript resolver](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/infrastructure/core/project_paths.py#L59-L75),
and [stage commands](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/docs/RUN_GUIDE.md#L563-L574).
