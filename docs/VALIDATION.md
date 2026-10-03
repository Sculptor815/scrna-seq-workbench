# Validation and known limitations

Version 0.3.0 adds a biological-question entry point and a focused donor-expression
command. The main branch contains the analysis plugin; the benchmark branch adds
developer scoring. New synthetic tests check equal donor weighting, count preservation,
missing groups, paired observations, output provenance and the absence of a scoring
command from the analysis runner. Historical scores are preserved and human HPA
review is pending. No real-data research improvement is claimed from these checks.
Local checks are recorded in [validation.json](../validation.json); each pushed
commit has its own [Actions results](https://github.com/Sculptor815/scrna-seq-workbench/actions).

Live conversations in Codex, Claude Code and DeepSeek Harness have not all been
accepted. Clean-machine GPU or remote-cluster execution is not claimed.

## Engineering checks

Structural checks cover release versions, marketplace paths, English Markdown,
relative Markdown/HTML links, Harness adapter synchronization and Python syntax.
The benchmark verifier checks 37 frozen source files, 69 committed artifacts,
five dimension records, 20 metric rows and 23,735 seed-0 cells. It independently
recalculates broad-label agreement and coverage from the committed coordinate
tables. Original counts and model training remain outside that offline check.

The regression suite covers counts, metadata, QC, annotation, donor aggregation
and tamper/dimension failures. A restricted local Windows environment still blocks
six existing tests that use private temporary directories. The previous release's
[Windows and Linux run](https://github.com/Sculptor815/scrna-seq-workbench/actions/runs/37012273297)
passed; new commits need their own CI result. Synthetic execution checks use
artificial data and measure whether the workflow executes.

## Earlier local biological evaluation

A frozen v0.1.0 configuration was run on five independent public studies: Kang
2018, Haber 2017, Paul 2015, Zeisel 2015 and Baron 2016. Each used a PCA baseline
and three scVI seeds, at most 6000 QC-passing cells and a 100-epoch CPU training cap.
The repository includes historical metrics, derived comparison tables and the
frozen source archive. Raw matrices and fitted models remain external; reproducing
the complete training run requires those inputs and an appropriate environment.

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
