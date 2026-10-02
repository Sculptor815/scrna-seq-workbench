# Five-study development benchmark

See [the visual comparisons](../docs/COMPARISONS.md). These five studies are now development data; future generalization claims require unseen studies.

## Two distinct records

`legacy/` preserves the numerical baseline: per-sample example QC (minimum 200 genes), PCA and scVI (seeds 0, 1, 2; 100-epoch CPU cap), maximum 6,000 randomly selected passing cells per study, and fixed tissue marker panels. No forced batch correction was tested. Its protocol, data URLs, download hashes, source hashes, 20-run metrics and count-preservation record are committed unchanged.

`evidence/` adds the current HPA-guided marker measurements, heatmaps and pending review forms using the existing seed-0 embeddings. The new proposal computation was checked against the historical predictions. Reference labels were joined only after proposal generation. **There are no completed human HPA reviews, and no new HPA annotation accuracy score.** Reusing embeddings is not retraining scVI or reproducing HPA's PCA workflow.

## Verify the published record

```text
python scripts/verify_benchmark.py
```

Run from the repository root. This offline check compares the 37 members of
`frozen/plugin-v0.1.0.zip` against the original `legacy/plugin_source_hashes.json`.
It also checks the committed artifact hashes/inventory, five stage-dimension
records, 20 metric rows and seed-0 annotation agreement/coverage for 23,735 cells.
It reads `integrity_manifest.json` and does not write to the repository.

The ZIP preserves the original source bytes, including historical documentation.
Its purpose is provenance; the active plugin remains under `plugins/`.
Text-table hashes normalize CRLF to LF for cross-platform checkouts. ZIP hashes
use exact bytes. The verifier reports committed-file consistency, while the old
`legacy/integrity_checks.json` records checks made during the original runs.
Neither record is independent proof of historical execution.

The input manifest's `genes` field is the **pre-QC** dimension. In `qc_summary.csv`,
`genes_in` matches it and `genes_out` is the smaller post-QC dimension used by the
model. [dimensions.json](dimensions.json) records the observed H5AD shapes and
hashes. [The review response](../docs/REVIEW_FIXES.md) explains the apparent mismatch.

Dataset citations, derivative scope and explicitly unverified license fields are
in [dataset_sources.json](dataset_sources.json). The current evidence uses neutral
cell IDs. The original-ID Haber audit mentioned in the older package review is
not part of this repository.

| Study | Species / tissue | Key development finding |
|---|---|---|
| Kang 2018 | Human PBMC | Example QC retained only 22 of 132 reference megakaryocytes; T/NK ambiguity |
| Haber 2017 | Mouse intestine | Stem/progenitor ambiguity; the 200-gene baseline differs from the paper's 800-gene droplet rule |
| Paul 2015 | Mouse myeloid progenitors | Limited panel coverage and developmental-state errors |
| Zeisel 2015 | Mouse brain | Broad versus fine labels and merged classes need care |
| Baron 2016 | Human pancreas | High overall agreement hides rare-type errors |

These processed copies lack matching mitochondrial symbols. They do not test removal of all originally low-quality cells. Paper-versus-copy cell sets differ for some studies. The author labels are silver standards, not independent truth. There is no claim about real condition-DE FDR, GPU behavior or autonomous host decisions.

## Review without label leakage

Give the annotating agent only the counts, tissue information, panel and marker packet. Withhold `embedding.csv` reference columns, original author-labeled figures and per-type evaluation tables until decisions are frozen. Original paper marker definitions may be a documented prior, but using author cluster identities to choose the answer invalidates an independent annotation evaluation.

Complete the per-cluster review according to [the policy](../plugins/scrna-seq-workbench/references/hpa-guided-annotation.md). Resolve mixed clusters through a separate documented analysis when appropriate. Lock the final review file and its hash, then score both main and detailed types, Unknown coverage, rare-type recall, macro-F1, confusion matrices and QC retention. Do not drop Unknown cells from the primary denominator.

## Reproducing the presentation and evidence

```text
python scripts/render_comparisons.py --outdir work/comparisons
python scripts/build_benchmark_evidence.py --benchmark-work PATH_TO_EXISTING_RUNS --outdir work/new-evidence
```

The first command needs only the committed tables. The second requires the original frozen run directory with each study's `scvi_0_annotation/annotated.h5ad`, `panel.json` and quarantined `reference_labels.csv`; those large artifacts are not bundled. Both commands write to fresh output directories and reject destinations within the committed evidence or documentation. Evidence generation also rejects destinations inside the input runs. This repository does not yet offer a one-command recreation of the historical model training from fresh downloads. Dataset URLs and hashes identify the required source copies.

Original paper images are externally linked with source captions; two source assets remain unavailable. All five same-coordinate author-label versus plugin-label comparisons are generated locally and clearly distinguished from original figures.
