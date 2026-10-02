# Review response: v0.2.1

The external review examined a local v0.1.1 package. This revision applies the
findings to the published v0.2.0 repository and records the evidence for each
resolution. Historical scores and review decisions are unchanged.

| Finding | Resolution |
|---|---|
| Preparation rewrites its own expected source hashes | The current repository has no baseline preparation command. It now includes the original v0.1.0 source ZIP and a verifier that only reads committed expectations. All 37 source files were matched to the existing historical hashes before packaging. |
| Input and output gene counts appear inconsistent | The two counts describe different stages. Original H5AD shapes and QC reports confirm the input counts and the smaller gene axes after QC. `dimensions.json` names and hashes each stage. The old data manifest remains unchanged. |
| Version drift and obsolete publishing text | v0.2.1 is recorded in all plugin manifests, the Claude catalog, README, citation and release notes. Package validation checks these together. Publishing instructions now describe updates to the existing repository. |
| Reproduction overwrites committed evidence | Figure rendering defaults to a new `work/comparisons` directory. Both evidence generation and rendering reject protected benchmark/documentation output paths. Existing output directories are refused. |
| Missing dataset attribution/license information | `dataset_sources.json` records each study, DOI, copy source, transformations, distributed derivatives and license status. Dataset-specific licenses remain unverified and are explicitly recorded as such. |
| Benchmark checks absent from CI | Both operating-system jobs run `verify_benchmark.py`, which verifies the source ZIP, artifact inventory/hashes, stage dimensions and seed-0 agreement/coverage against the historical metrics. |
| A lower mitochondrial percentage bound is suggested | Mitochondrial MAD summaries now give only an upper bound. Count/gene summaries retain both bounds. Applied filters and historical results are unchanged. |

## Gene counts, checked against the saved H5AD files

| Study | Before QC | After QC / model input |
|---|---:|---:|
| Kang | 15,706 | 15,701 |
| Haber | 15,215 | 14,600 |
| Paul | 8,716 | 8,716 |
| Zeisel | 19,972 | 18,879 |
| Baron | 20,125 | 16,359 |

The benchmark QC config retains genes expressed in at least three retained cells.
The prepared gene mappings contained no duplicate analysis symbols in these saved
runs. The differences above therefore do not indicate duplicate-symbol aggregation
or a stale input manifest. Model inputs then cap cells at 6,000 without changing
the QC gene axis. See [the dimension audit](../benchmarks/dimensions.json).

## What the new checks establish

The verifier compares the frozen archive with the 37 hashes already present in
v0.2.0. It never regenerates those expectations. Text artifact hashes normalize
CRLF to LF so checkout line endings do not change the result; frozen ZIP members
use their original bytes. The archive remains a historical reference and is not
installed as the active plugin.

These checks detect accidental changes to the committed evidence and confirm
agreement between records. They do not recreate model training, prove which code
was executed in the past, or provide an external cryptographic signature. The
historical `integrity_checks.json` is retained as a run-time record; current
verification reports its own scope separately.

## Remaining limits

Raw count matrices and trained models are external to the repository. A full
training rerun still requires those inputs and a separately recorded environment.
Dataset redistribution terms need confirmation from the original sources before
they can be represented by specific license identifiers. Live acceptance sessions
in all three hosts and completed human review of the five annotation packets
remain future work.
