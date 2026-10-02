# Validation and known limitations

Version 0.2.0 adds HPA-guided evidence and review validation plus five-study figures.
It preserves historical scores; manual review is pending. Local validation is
recorded in [validation.json](../validation.json). GitHub CI results are visible on
the repository Actions page after publication. Do not assume a configured workflow passed.

Live conversations in Codex, Claude Code and DeepSeek Harness have not all been
accepted. Clean-machine GPU or remote-cluster execution is not claimed.

## Engineering checks

Structural checks cover manifest identity/version consistency, English Markdown,
relative links, generated Harness adapter synchronization and Python syntax.
The core suite exercises counts validation, metadata alignment, filtering and
marker/DE boundary cases. Synthetic execution checks use artificial truth and
cannot establish scientific accuracy. GitHub CI must run after publication.

## Earlier local biological evaluation

A frozen v0.1.0 configuration was run on five independent public studies: Kang
2018, Haber 2017, Paul 2015, Zeisel 2015 and Baron 2016. Each used a PCA baseline
and three scVI seeds, at most 6000 QC-passing cells and a 100-epoch CPU training cap.
Those historical data, model files and detailed results are not bundled in this
minimal source release. This is a summary, not a reproducible benchmark submission.

| Study | Broad-label agreement range, scVI |
|---|---:|
| Kang, human PBMC | 79.6-85.3% |
| Haber, mouse intestinal epithelium | 56.7-63.9% |
| Paul, mouse myeloid progenitors | 44.0-52.6% |
| Zeisel, mouse brain | 76.6-77.8% |
| Baron, human pancreas | 95.6-96.4% |

Agreement is with coarse silver-standard labels, counting Unknown as a miss;
it is not biological truth accuracy. Tissue panels beyond PBMC were configured by
the analyst. The runs did not evaluate autonomous host decisions or batch correction.

Observed failures include major loss of low-RNA reference megakaryocytes under the
example QC floor (132 to 22 cells), T/NK and stem/progenitor ambiguity, missing
marker coverage, rare-type failures hidden by high overall agreement, and limited
seed stability. The filtered public copies lacked matching mitochondrial gene
symbols, so MT-QC quality could not be evaluated. Some original paper thresholds
and source-version differences remain unresolved. The intake update does not fix
these numerical limitations by itself.

## Use boundaries

Raw integer UMI provenance is required. A matrix with only normalized values is not
a valid substitute. Default parameters are examples, not tissue-specific validation.
UMAP is a visualization. HPA support derives candidate markers from a supplied
human nCPM table; it does not reproduce HPA's complete processing/annotation pipeline.
Reference scores are not calibrated probabilities. Annotation proposals need review.

Real-data report parsing across vendors, doublet detection performance, annotation
generality, condition-DE FDR/power and additional DE covariates need separate testing.
Only the documented simple paired/unpaired designs are implemented. Three donors is
an operational minimum, not a power guarantee. Do not replace donor-level DE with
cell-level testing when its prerequisites fail.
