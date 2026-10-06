# External scRNA-seq experience: owner review packet

Read the [scope and access limits](README.md) first. Prepared 2026-10-06. Every entry is pending owner review.

<a id="r01"></a>

## R01: Use the current tutorial location and record the version

### Source observation

The old Scanpy tutorial repository is archived and points to tutorial sources in the main repository. scvi-tutorials separately hosts scvi-tools notebook sources.

### Our proposed rule, for review

Log the tutorial URL, access date, installed package versions and a commit or release when available. Check whether an example is current or explicitly legacy before adapting it.

### Applicability and limitations

Repository location is provenance, not a scientific quality score. A directory listing does not establish that all notebooks have been evaluated.

### Relationship to the current plugin

Documentation improvement only; existing analysis commands are unchanged.

### Question for the researcher

Which tutorials should we maintain as supported examples, and which should remain historical reading?

### Proposed acceptance check (not yet executed)

A proposed workflow cites its specific source and environment rather than claiming compatibility from the repository name.

### Sources

- **S20** [Archived Scanpy tutorials repository](https://github.com/scverse/scanpy-tutorials) — official_repository. Location: Archive banner and README relocation links. Access: readme_and_listing_read. Page reports archival on 2026-08-18 and points to main Scanpy docs.
- **S21** [Current Scanpy tutorial source directory](https://github.com/scverse/scanpy/tree/main/docs/tutorials) — official_repository. Location: Directory listing. Access: listing_read. Current source location located; not a claim that every notebook was read.
- **S12** [scvi-tutorials](https://github.com/scverse/scvi-tutorials) — official_repository. Location: README; quick_start and scrna directory listing. Access: readme_and_listing_read. Notebook source repository located; complete notebooks not executed or exhaustively reviewed.

**Owner decision:** pending. **Reviewer/date:** unassigned. **Production retrieval:** ineligible.

<a id="r02"></a>

## R02: Inspect QC per sample and revisit exclusions

### Source observation

The Scanpy tutorial recommends inspecting sample-specific QC distributions and revisiting permissive initial filtering after examining the data structure.

### Our proposed rule, for review

Before adopting a cutoff, record the sample-level distribution and the affected populations. Compare a small, justified alternative and retain both exclusion ledgers.

### Applicability and limitations

Applies to cell filtering. A permissive first pass is exploratory and does not mean every retained cell is suitable for final inference.

### Relationship to the current plugin

Existing inspect-only mode, per-sample filters and ledgers support this review. Population-aware sensitivity reporting is still manual.

### Question for the researcher

Which tissue-specific evidence would make you retain a low-complexity population or remove it?

### Proposed acceptance check (not yet executed)

Compare retained cells by sample and candidate population under two predeclared settings; explain losses, not only the final UMAP.

### Sources

- **S01** [Scanpy preprocessing and clustering](https://scanpy.scverse.org/en/stable/tutorials/basics/clustering.html) — official_tutorial. Location: Quality Control; Doublet detection; Normalization. Access: page_read. Live stable documentation; examples are dataset-specific.

**Owner decision:** pending. **Reviewer/date:** unassigned. **Production retrieval:** ineligible.

<a id="r03"></a>

## R03: Do not transfer a MAD multiplier without its definition

### Source observation

The QC chapter applies MAD rules to transformed QC metrics. Its example is not numerically identical to our raw-metric suggestion implementation.

### Our proposed rule, for review

Record the metric transformation, MAD scaling convention, multiplier and whether the result is merely suggested or applied.

### Applicability and limitations

Robust outlier rules still need tissue and sample context. Equal multipliers do not imply equal thresholds when conventions differ.

### Relationship to the current plugin

Our suggestions use median plus/minus 3 times 1.4826 times MAD on recorded metrics and are not automatically applied. Do not silently replace them with the chapter recipe.

### Question for the researcher

Should we compare raw and log-scale QC suggestions for each tissue, and how would you decide between them?

### Proposed acceptance check (not yet executed)

On a fixed QC vector, explicitly compute both definitions and compare which cells change status.

### Sources

- **S02** [Single-cell best practices: QC](https://www.sc-best-practices.org/preprocessing-visualization/quality-control/) — author_maintained_tutorial. Location: QC metrics and MAD example; ambient RNA; min_cells=20; doublet section. Access: page_read. Living chapter. Broad summaries and individual code examples need separate interpretation.

**Owner decision:** pending. **Reviewer/date:** unassigned. **Production retrieval:** ineligible.

<a id="r04"></a>

## R04: Define the physical capture before detecting doublets

### Source observation

The tutorials run doublet detection with sample/batch separation rather than treating independent captures as one mixture.

### Our proposed rule, for review

Resolve capture IDs before detection. Inspect scores alongside competing markers and cell quality, and record the expected-rate assumption.

### Applicability and limitations

Capture, donor and condition are not automatically interchangeable. A doublet call and ambient RNA contamination require different investigations.

### Relationship to the current plugin

Current optional Scrublet runs by capture and requires sufficient eligible cells; scDblFinder is not implemented.

### Question for the researcher

How are captures, pooled donors and multiplexing recorded in your experiments?

### Proposed acceptance check (not yet executed)

A dataset with two captures is processed with the correct grouping; cells with conflicting markers receive an evidence review rather than automatic identity claims.

### Sources

- **S01** [Scanpy preprocessing and clustering](https://scanpy.scverse.org/en/stable/tutorials/basics/clustering.html) — official_tutorial. Location: Quality Control; Doublet detection; Normalization. Access: page_read. Live stable documentation; examples are dataset-specific.
- **S02** [Single-cell best practices: QC](https://www.sc-best-practices.org/preprocessing-visualization/quality-control/) — author_maintained_tutorial. Location: QC metrics and MAD example; ambient RNA; min_cells=20; doublet section. Access: page_read. Living chapter. Broad summaries and individual code examples need separate interpretation.

**Owner decision:** pending. **Reviewer/date:** unassigned. **Production retrieval:** ineligible.

<a id="r05"></a>

## R05: Treat ambient RNA correction as a separate, auditable branch

### Source observation

SoupX documents a channel-level workflow with droplet and cell-count inputs, clustering information, contamination estimation and adjusted counts.

### Our proposed rule, for review

First establish suitable source matrices and contamination evidence. If tested, save corrected counts separately and compare selected markers and downstream conclusions with the uncorrected branch.

### Applicability and limitations

This is a candidate extension, not a requirement for every dataset. A filtered matrix alone may not provide the demonstrated input context.

### Relationship to the current plugin

SoupX is not installed as a plugin tool. No correction or matrix replacement is authorized by this note.

### Question for the researcher

Which marker patterns and negative controls would convince you that apparent expression is contamination?

### Proposed acceptance check (not yet executed)

Predeclare diagnostic genes and evaluate correction magnitude and biological signal preservation, retaining both matrices and method versions.

### Sources

- **S03** [SoupX](https://github.com/constantAmateur/SoupX) — method_author_repository. Location: README Quickstart; SoupChannel and setClusters; version notes. Access: readme_read. README reviewed; code not executed and no release pinned.

**Owner decision:** pending. **Reviewer/date:** unassigned. **Production retrieval:** ineligible.

<a id="r06"></a>

## R06: Validate every component before combining matrices

### Source observation

A forum reporter inspected early rows, missed a normalized dataset later in a concatenated object, and subsequently identified that mixed representation as the cause of count warnings.

### Our proposed rule, for review

Validate each source dataset before concatenation and inspect all stored nonzero values in bounded chunks, alongside processing provenance. Do not round transformed values into counts.

### Applicability and limitations

This is a firsthand debugging case, not evidence that every fractional matrix has the same origin. Some assays or quantifiers produce fractional values legitimately.

### Relationship to the current plugin

Existing numeric count checks help reject incompatible values; future multi-matrix intake needs per-source provenance. Multi-matrix assembly is outside the current runner.

### Question for the researcher

Which processing records should be mandatory when a collaborator supplies a merged H5AD?

### Proposed acceptance check (not yet executed)

A fixture with a normalized block at the end fails intake even though its initial rows appear count-like.

### Sources

- **S04** [Normalized data found instead of raw counts](https://discourse.scverse.org/t/normalized-data-found-instead-of-raw-counts/2163) — community_firsthand_case. Location: Posts 1-3, 15-18 March 2024. Access: thread_read. Reporter confirmed a normalized dataset hidden at the end of a concatenated object.

**Owner decision:** pending. **Reviewer/date:** unassigned. **Production retrieval:** ineligible.

<a id="r07"></a>

## R07: A raw slot is not a verified raw-count archive

### Source observation

The AnnData excerpt initializes raw with a copy; a historical issue reports unexpected mutation after assignment. The scvi-tools tutorial also uses raw for normalized values.

### Our proposed rule, for review

Document representation explicitly, preserve a separate counts copy and verify that later transformations do not modify it. Do not infer numeric meaning from the attribute name.

### Applicability and limitations

The historical issue is not reproduced here. The AnnData page was only available as an indexed official excerpt; review current-version behavior before accepting a precise copy contract.

### Relationship to the current plugin

The plugin uses a named counts layer and independently retained input files rather than relying on raw as proof of provenance.

### Question for the researcher

What representation names and checks should every imported H5AD provide?

### Proposed acceptance check (not yet executed)

Hash the source file and compare retained counts before and after normalization/representation fitting; inspect any raw attribute independently.

### Sources

- **S05** [AnnData.raw](https://anndata.readthedocs.io/en/latest/generated/anndata.AnnData.raw.html) — official_api. Location: Initialization with a copy; slicing behavior. Access: search_excerpt_only. Direct page retrieval failed. Latest/dev documentation excerpt only; verify installed version before adoption.
- **S06** [AnnData raw mutation report](https://github.com/scverse/scanpy/issues/3073) — issue_firsthand_case. Location: Issue body, May 2024; closed issue linked to anndata #1686. Access: issue_body_read. Historical issue; not evidence that current versions still have this behavior.
- **S11** [scvi-tools data loading and preparation](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/quick_start/data_loading.html) — official_tutorial. Location: Preprocessing; preserve counts; register layer and batch. Access: page_read. Tutorial demonstrates multiple representations; model-specific contracts still apply.

**Owner decision:** pending. **Reviewer/date:** unassigned. **Production retrieval:** ineligible.

<a id="r08"></a>

## R08: Select the HVG input layer to match the method

### Source observation

The official indexed API distinguishes logarithmized inputs from count-based seurat_v3 flavors. A technical forum reply explains explicit layer selection when normalization has already occurred in X.

### Our proposed rule, for review

Validate the representation of the selected layer and record flavor, batch key and feature set. Changing method names without changing the input contract is not a valid comparison.

### Applicability and limitations

The current API page was only available as an indexed excerpt. A 2023 cross-tool comparison does not prove equality across present versions or batch-ranking options.

### Relationship to the current plugin

The runner already uses the counts layer for seurat_v3 and log-normalized X for its seurat option.

### Question for the researcher

Which biological signals should remain represented when alternative HVG choices are compared?

### Proposed acceptance check (not yet executed)

A deliberately log-normalized counts layer is rejected; two valid HVG strategies are compared with feature overlap and downstream stability, not only runtime.

### Sources

- **S07** [Scanpy highly_variable_genes](https://scanpy.scverse.org/en/stable/generated/scanpy.pp.highly_variable_genes.html) — official_api. Location: Input expectations; flavor and layer. Access: search_excerpt_only. Direct retrieval was rate-limited; exact input requirement available in indexed official excerpt.
- **S08** [HVG flavor and normalization order](https://discourse.scverse.org/t/how-to-handle-data-lognormalization-when-using-highly-variable-genes-with-flavor-seurat-v3/1076) — community_technical_reply. Location: Posts 1-3, January-February 2023. Access: thread_read. Layer selection clarified; historical cross-tool comparison is not a current equivalence guarantee.

**Owner decision:** pending. **Reviewer/date:** unassigned. **Production retrieval:** ineligible.

<a id="r09"></a>

## R09: Record the normalization target instead of saying only normalized

### Source observation

The normalize_total API documents that target_sum=None uses the median original cell total.

### Our proposed rule, for review

Record the target, transformation and gene universe used in its denominator. Inspect downstream tool contracts before reusing the matrix.

### Applicability and limitations

Median scaling and CP10k need not yield the same transformed numbers. Neither is automatically better for every downstream task.

### Relationship to the current plugin

Our plugin explicitly uses CP10k followed by log1p. This differs from a tutorial call that leaves target_sum unspecified.

### Question for the researcher

Should all project outputs carry a machine-readable representation label including the normalization target?

### Proposed acceptance check (not yet executed)

For a small fixed count matrix, recover the chosen normalized totals before log1p and verify that later tools consume the intended layer.

### Sources

- **S09** [Scanpy normalize_total](https://scanpy.scverse.org/en/stable/generated/scanpy.pp.normalize_total.html) — official_api. Location: target_sum and layer parameters. Access: page_read. Default target_sum=None uses median pre-normalization cell total.

**Owner decision:** pending. **Reviewer/date:** unassigned. **Production retrieval:** ineligible.

<a id="r10"></a>

## R10: Check the classifier input and reference before trusting labels

### Source observation

CellTypist documents log1p CP10k AnnData input and recommends retaining broad gene coverage for overlap with its trained model.

### Our proposed rule, for review

If adding a classifier, record model identity, training scope and gene overlap; compare proposals with marker evidence and retain an unresolved option.

### Applicability and limitations

This contract belongs to CellTypist, not every annotation method. Correct input formatting does not establish tissue or disease-state validity.

### Relationship to the current plugin

Current annotation is marker-based and reviewed; CellTypist is a possible separate tool, not an existing backend.

### Question for the researcher

Which tissues or novel states would require rejecting or broadening an automated reference label?

### Proposed acceptance check (not yet executed)

Test known reference-compatible cells alongside an intentionally out-of-scope population and review both, without forcing every prediction into a final label.

### Sources

- **S10** [CellTypist](https://github.com/Teichlab/celltypist) — method_author_repository. Location: README section 1.6: Celltyping based on AnnData. Access: readme_read. AnnData input contract reviewed; not installed or tested in our plugin.

**Owner decision:** pending. **Reviewer/date:** unassigned. **Production retrieval:** ineligible.

<a id="r11"></a>

## R11: Register counts and batch deliberately for scVI

### Source observation

The scvi-tools preparation tutorial preserves counts and explicitly registers the count layer and batch key for SCVI.

### Our proposed rule, for review

Validate what each covariate represents before fitting. Keep an uncorrected comparison and assess both unwanted variation and biological signal retention.

### Applicability and limitations

Only the relevant preparation sections and repository overview were inspected; this is not a completed integration benchmark. Batch correction cannot establish causality.

### Relationship to the current plugin

Existing scVI setup registers counts and batch; PCA remains an uncorrected baseline. Our runner does not expose every covariate option in scvi-tools.

### Question for the researcher

When disease and processing batch overlap, what evidence would you require before interpreting a corrected representation?

### Proposed acceptance check (not yet executed)

Record sample-design tables and examine donor, condition and marker patterns in both representations; flag non-identifiable comparisons.

### Sources

- **S11** [scvi-tools data loading and preparation](https://docs.scvi-tools.org/en/stable/tutorials/notebooks/quick_start/data_loading.html) — official_tutorial. Location: Preprocessing; preserve counts; register layer and batch. Access: page_read. Tutorial demonstrates multiple representations; model-specific contracts still apply.
- **S12** [scvi-tutorials](https://github.com/scverse/scvi-tutorials) — official_repository. Location: README; quick_start and scrna directory listing. Access: readme_and_listing_read. Notebook source repository located; complete notebooks not executed or exhaustively reviewed.

**Owner decision:** pending. **Reviewer/date:** unassigned. **Production retrieval:** ineligible.

<a id="r12"></a>

## R12: Do not turn one donor into many biological replicates

### Source observation

The forum thread asks how to test two conditions with one replicate each and contains no visible answer. The primary paper excerpt examines biological-replicate aggregation and pseudo-replicates.

### Our proposed rule, for review

Check independent donors before population-level condition inference. With inadequate replication, present a restricted descriptive comparison and a request for suitable samples.

### Applicability and limitations

The unanswered question is not a validated workaround. The paper was available only through its indexed original-article excerpt in this pass; full Methods review remains outstanding.

### Relationship to the current plugin

Existing DE enforces donor gates. Those software floors do not guarantee power or remove confounding.

### Question for the researcher

What limited result would still help a researcher when replication is insufficient?

### Proposed acceptance check (not yet executed)

Randomly splitting a donor into cell subsets must not satisfy the donor gate; the report must identify the true experimental unit.

### Sources

- **S14** [DE with one replicate per condition](https://discourse.scverse.org/t/questions-about-how-to-do-de-with-one-replicate-for-one-sample/2421) — community_question. Location: Original question, 31 July 2024. Access: thread_read. Fetched page contains the question but no answer; not a validated workaround.
- **S16** [Confronting false discoveries in single-cell differential expression](https://www.nature.com/articles/s41467-021-25960-2) — primary_research. Location: Indexed original article: biological-replicate aggregation and pseudo-replicate comparison. Access: search_excerpt_only. Original full page failed retrieval this pass. Read full Methods before scientific sign-off.

**Owner decision:** pending. **Reviewer/date:** unassigned. **Production retrieval:** ineligible.

<a id="r13"></a>

## R13: Separate marker ranking from replicated condition DE

### Source observation

The rank_genes_groups API expects logarithmized data and warns about non-independent cells in inferential comparisons.

### Our proposed rule, for review

Label exploratory cluster-marker ranking separately from donor-level condition testing. Explicitly identify the matrix, grouping, reference and experimental unit.

### Applicability and limitations

A marker-ranking function can be useful without providing a valid population-level condition test. Raw-count expectations depend on the method, not the word DE.

### Relationship to the current plugin

The plugin uses exploratory marker evidence for annotation and a separate raw-count pseudobulk path for condition DE.

### Question for the researcher

What wording should distinguish a candidate marker from a replicated disease-associated gene in reports?

### Proposed acceptance check (not yet executed)

A report must not present cell-level marker p-values as donor-replicated evidence; trace every contrast to its design and representation.

### Sources

- **S15** [Scanpy rank_genes_groups](https://scanpy.readthedocs.io/en/stable/generated/scanpy.tl.rank_genes_groups.html) — official_api. Location: Input requirement and independence warning. Access: page_read. Group-marker ranking is not a substitute for a donor-aware condition model.

**Owner decision:** pending. **Reviewer/date:** unassigned. **Production retrieval:** ineligible.

<a id="r14"></a>

## R14: Review low-expression DE instead of importing a forum cutoff

### Source observation

In a scVI discussion, a user reports rare-gene DE calls; a reply contrasts the user's 30% detection filter with a personal 5% choice and another model-scale filter.

### Our proposed rule, for review

Inspect observed counts, detection, donor consistency and effect estimates together. Predeclare any expression filter and investigate sensitivity rather than selecting a favorable result.

### Applicability and limitations

These are scVI-specific experiences, not a validated universal 5% cutoff or a rule for PyDESeq2. Filtering only HVGs can also change which hypotheses are tested.

### Relationship to the current plugin

Our condition DE uses pseudobulk/PyDESeq2, so the forum thresholds must not be inserted directly.

### Question for the researcher

How would you distinguish a rare but meaningful transcript from an unstable low-signal finding?

### Proposed acceptance check (not yet executed)

Keep both unfiltered and explicitly filtered result tables and explain which conclusions depend on the filter.

### Sources

- **S17** [Differential expression and rarely expressed genes](https://discourse.scverse.org/t/differential-expression-and-rarely-expressed-genes/1998) — community_experience. Location: Posts 1-2, January 2024. Access: thread_read. Reply gives scVI-specific personal filtering choices, not a universal detection threshold.

**Owner decision:** pending. **Reviewer/date:** unassigned. **Production retrieval:** ineligible.

<a id="r15"></a>

## R15: Review a tutorial design formula against the sampling scheme

### Source observation

The chapter describes eight patients in both conditions, constructs patient-condition pseudobulks, then shows a ~label model and motivates excluding patient terms using PCA patterns.

### Our proposed rule, for review

Flag this example for statistical review before adoption. Specify paired or unpaired design from sampling metadata; PCA alone should not decide whether repeated observations are independent.

### Applicability and limitations

This is our methodological concern about the displayed example, not a reproduction of its results or a claim that every conclusion in the chapter is wrong.

### Relationship to the current plugin

Our paired path uses ~donor+condition; this note does not alter it. Designs beyond the runner's formulas require a separate implementation.

### Question for the researcher

Do you agree that the example needs an explicit paired-design discussion? Which comparison should we reproduce?

### Proposed acceptance check (not yet executed)

On a suitable paired example, compare estimable design matrices and effect uncertainty with and without donor terms, with statistical review of the contrast.

### Sources

- **S13** [Single-cell best practices: differential gene expression](https://www.sc-best-practices.org/conditions/differential-gene-expression/) — author_maintained_tutorial. Location: Pseudobulking; Variability Exploration; PyDESeq2 formula. Access: page_read. Current example uses ~label despite describing paired patient-condition samples; review concern recorded, not silently adopted.

**Owner decision:** pending. **Reviewer/date:** unassigned. **Production retrieval:** ineligible.

<a id="r16"></a>

## R16: Treat historical memory workarounds as version-specific

### Source observation

A 2020 issue reports a backed-mode log1p/copy error with explicit old Scanpy and AnnData versions.

### Our proposed rule, for review

Before applying a workaround, reproduce a minimal case in the installed environment and estimate memory cost. Preserve the original file and capture the actual traceback.

### Applicability and limitations

The old report does not establish a current bug or imply that loading everything into memory is safe.

### Relationship to the current plugin

The current runner is not an out-of-core pipeline. A large-data execution path would need its own resource controls and tests.

### Question for the researcher

What memory ceiling and fallback behavior would be acceptable on your workstation?

### Proposed acceptance check (not yet executed)

An oversized job should provide a resource explanation rather than blindly densifying or replacing the source file.

### Sources

- **S18** [log1p on backed H5AD copy error](https://github.com/scverse/scanpy/issues/1153) — issue_firsthand_case. Location: Issue body and reported package versions, April 2020. Access: issue_body_read. Old version-specific reproduction; current status was not reproduced locally.

**Owner decision:** pending. **Reviewer/date:** unassigned. **Production retrieval:** ineligible.

<a id="r17"></a>

## R17: Choose an enrichment background that matches gene eligibility

### Source observation

GO guidance allows a reference/background list and explains that enrichment compares the submitted list against that reference.

### Our proposed rule, for review

Define eligible genes, mapping losses, selection criteria, database release and multiple-testing scope before interpretation. Inspect the genes driving each term.

### Applicability and limitations

An enrichment result is not itself a functional activity measurement or causal experiment. Ranked-list methods require their own contracts.

### Relationship to the current plugin

Enrichment remains a future extension; no GO/KEGG/Reactome analysis tool was added in this collection.

### Question for the researcher

For your biological question, which genes could genuinely have entered the selected list?

### Proposed acceptance check (not yet executed)

Compare justified background choices and flag terms whose interpretation changes; do not silently default to the whole genome.

### Sources

- **S19** [GO enrichment analysis](https://geneontology.org/docs/go-enrichment-analysis/) — official_method_guidance. Location: Gene lists and reference/background list. Access: page_read. Guidance for enrichment; not evidence of pathway activation.

**Owner decision:** pending. **Reviewer/date:** unassigned. **Production retrieval:** ineligible.

<a id="r18"></a>

## R18: Distinguish global gene filtering from test-specific filtering

### Source observation

The Scanpy introduction uses a three-cell gene filter; the QC chapter later uses twenty cells; the DE chapter applies additional pseudobulk expression filters.

### Our proposed rule, for review

Record the stage, unit and purpose of every filter. Review whether a global filter removes genes needed for a rare population before applying a downstream test-specific filter.

### Applicability and limitations

These example thresholds are not interchangeable recommendations. A rare-cell marker can be lost under a global rule even when useful within its population.

### Relationship to the current plugin

Current QC defaults to detection in three retained cells; DE applies a separate aggregated-count filter. Changes require a reviewed case and implementation test.

### Question for the researcher

Which rare populations or targeted genes should we explicitly monitor when assessing gene-filter sensitivity?

### Proposed acceptance check (not yet executed)

Compare retained targeted genes and rare-population evidence under justified settings; preserve each tested gene universe in the report.

### Sources

- **S01** [Scanpy preprocessing and clustering](https://scanpy.scverse.org/en/stable/tutorials/basics/clustering.html) — official_tutorial. Location: Quality Control; Doublet detection; Normalization. Access: page_read. Live stable documentation; examples are dataset-specific.
- **S02** [Single-cell best practices: QC](https://www.sc-best-practices.org/preprocessing-visualization/quality-control/) — author_maintained_tutorial. Location: QC metrics and MAD example; ambient RNA; min_cells=20; doublet section. Access: page_read. Living chapter. Broad summaries and individual code examples need separate interpretation.
- **S13** [Single-cell best practices: differential gene expression](https://www.sc-best-practices.org/conditions/differential-gene-expression/) — author_maintained_tutorial. Location: Pseudobulking; Variability Exploration; PyDESeq2 formula. Access: page_read. Current example uses ~label despite describing paired patient-condition samples; review concern recorded, not silently adopted.

**Owner decision:** pending. **Reviewer/date:** unassigned. **Production retrieval:** ineligible.
