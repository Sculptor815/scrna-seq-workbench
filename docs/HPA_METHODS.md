# What we adopt from HPA

The annotation contract is defined in [the shared policy](../plugins/scrna-seq-workbench/references/hpa-guided-annotation.md). Its source and access date are pinned there. The current website is a changing resource, so a future method change requires a new protocol version.

## QC and integration lessons

HPA's [methods overview](https://www.proteinatlas.org/humanproteome/single%2Bcell/single%2Bcell%2Btype/method) describes ambient-RNA correction, doublet/mitochondrial/outlier filtering, and tissue-aware protection of low-RNA and rare populations. Its [detailed methods](https://www.proteinatlas.org/humanproteome/single%2Bcell/single%2Bcell%2Btype/method/transcriptomics) describe reviewing excluded hematopoietic lineages, cluster-level expression aggregation and subsequent atlas normalization. These are distinct operations from donor-level differential expression.

| Workbench decision | Current implementation | Remaining work |
|---|---|---|
| Inspect each sample before filtering | Intake, distributions and per-sample configurations | Validate choices on unfiltered tissue-specific inputs |
| Audit low-RNA loss | Exclusion ledgers and benchmark retention by reference class | Evidence-based rescue needs separate review; never rescue using hidden benchmark truth |
| Handle ambient RNA | Record whether already corrected | No SoupX implementation; processed matrices cannot reconstruct the missing droplets |
| Assess doublets | Optional per-capture scoring | Not an exact implementation of HPA's staged filtering |
| Keep usable marker evidence | Missing-marker warnings and detection fractions | Additional tissue panels and gene-ID mapping validation |
| Use hierarchical annotation | Main/detail fields and an evidence-backed review gate | Populate reviewed labels; no automatic expert approval |
| Refine mixed clusters | Record subcluster decision | Explicit subset/reclustering workflow remains manual |
| Aggregate across studies | Ambiguous labels flagged as ineligible | HPA-style pCPM/TMM and atlas aggregation are not implemented |

Do not copy a tissue's published QC cutoffs to all five datasets. Do not apply HPA's human reference labels to mouse matrices. Do not turn a partial imitation into a claim of exact reproduction.

The existing five-study results remain a **legacy marker baseline**. The new packets follow the HPA-guided review contract, but they have no final human-approved HPA labels yet. We intentionally publish this distinction rather than retrofit the old benchmark description.
