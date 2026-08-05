# docs/ — bond-utilities (Q-BRANCH)

Agent- and developer-facing documentation for `bond-utilities`, Layer 0 of the
BOND suite. This directory holds the operating rules for working *inside* this
package. The scientific write-up of what the package computes lives in
[`../manuscript/`](../manuscript/README.md); the public-facing overview is the
package [`README.md`](../README.md).

Read in this order on a cold start:

1. [`agent_instructions.md`](agent_instructions.md) — the hard constraints. Read
   before touching anything.
2. [`architecture.md`](architecture.md) — module-by-module architecture, layer
   position, and why this package has no `MissionProvider`.
3. [`testing_philosophy.md`](testing_philosophy.md) — the zero-mock, real-data,
   deterministic doctrine and the guards that enforce it.

## Contents

| Document | What it holds | Audience |
| --- | --- | --- |
| [`AGENTS.md`](AGENTS.md) | Index, conventions, verification commands | All agents |
| [`agent_instructions.md`](agent_instructions.md) | The numbered hard constraints plus the pre-"done" checklist | All agents (read-first) |
| [`architecture.md`](architecture.md) | Layer position, MissionProvider boundary, per-module contracts, dependency shape, how to add a primitive | Developers & agents |
| [`testing_philosophy.md`](testing_philosophy.md) | Zero-mock policy, what we use instead of mocks, coverage mechanics, the falsifiable guards, per-file test map | Anyone writing tests |
| [`style_guide.md`](style_guide.md) | Code style rules and conventions | Anyone writing code |
| [`syntax_guide.md`](syntax_guide.md) | `{{VARIABLE}}` tokens, figure registry, citation keys | Manuscript editors |
| [`quickstart.md`](quickstart.md) | Five-minute first run of the CLIs and library | New users |
| [`output_conventions.md`](output_conventions.md) | `output/` layout, producers, regeneration rules | Anyone regenerating artifacts |

## The one-line version

Pure primitives in `src/bond_utilities/`, thin orchestrators in `scripts/`,
real-data tests with zero mocks, one seed determines everything, and every
number in the manuscript is generated rather than typed.
