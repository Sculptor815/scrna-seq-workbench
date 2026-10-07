# AI analysis 2: independent FL, YS and hESC analyses

**Source report:** Human_HSC_separate_v2 / Human_HSC_separate_report.html. **Run date:** 2026-10-07. **Status:** supplied second exploratory AI analysis; all proposals and cautious AI revisions remain pending human review.

[Original overview HTML](original/Human_HSC_separate_report.html) | [FL report](original/FL/FL_report.html) | [YS report](original/YS/YS_report.html) | [hESC report](original/hESC/hESC_report.html) | [Checksums](source_manifest.json)

This English summary preserves the supplied results and their existing internal controls without changing the manual baseline or assigning a new accuracy ranking. Download the Chinese HTML reports for browser viewing; images are embedded. Keep the three cohort subdirectories with the overview for report navigation. Other original links to local CSV/configuration files refer to supporting files that are not published here.

## Analysis design and parameters

FL and YS were fitted independently, and Day0/Day6 jointly formed the hESC unit. Each unit received independent gene filtering, HVG selection, PCA, graph construction, Leiden, UMAP, marker ranking and annotation. The source report states that the joint embedding was not merely split into three displays.

| Cohort | Retained cells | Retained genes | Independent clusters | Cautious Unknown fraction |
|---|---:|---:|---:|---:|
| FL | 17,677 | 20,431 | 28 | 23.6% |
| YS | 11,021 | 20,719 | 21 | 6.0% |
| hESC Day0/Day6 | 19,157 | 20,924 | 26 | 21.8% |

All 47,855 cells were retained, including 9,485 Day0 and 9,672 Day6 cells. Each cohort used CPU PCA, 2,000 HVGs (seurat), 30 components, 15 neighbors, Leiden resolution 1.0 and seed 0, without scVI, batch correction or downsampling. QC reused the inspected cell thresholds from the first run; gene detection was filtered within each cohort. The code was Workbench v0.3.0, snapshot prefix 429eae2. Exact AI model/version and full prompt history were not provided.

## FL findings

The cautious display reports 23.1% erythroid-like, 21.9% HSPC-like, 5.2% megakaryocyte-like and 23.6% Unknown cells. Clusters 4, 6, 7 and 21 contain 3,868 progenitor-like candidates. A 109-cell cluster has a strong cardiac-associated expression program, including TNNT2, ACTC1 and MYL7, but the report does not establish its anatomical origin or exclude sample admixture. Mixed lymphoid/progenitor and hepatic/erythroid evidence is retained as uncertainty.

![Original independent FL UMAP](original/FL/figures/01_independent_umap.png)

## YS findings

Reported cautious candidates include erythroid-like (23.3%), HSPC-like (20.3%), hepatic/endoderm-like (13.9%), monocyte/macrophage-like (11.9%), megakaryocyte-like (9.1%), stromal-like (9.2%) and endothelial-like (5.5%) programs, with 6.0% Unknown. Strong CD34/SPINK2 in clusters 2, 3 and 17 motivated broad progenitor-like candidates. Incomplete T-cell evidence prompted cautious treatment of relative-score T-lineage proposals. Early endothelial programs and low HOXA9 motivate finer progenitor assessment rather than confirmation of mature functional HSCs.

![Original independent YS UMAP](original/YS/figures/01_independent_umap.png)

## hESC findings

Most progenitor-like candidates are associated with Day0. Cluster 8 contains 833 cells (800 Day0 and 33 Day6) with CD34/SPINK2 evidence, without a claim of mature HSC function. Erythroid-like fractions are approximately 54.7% and 16.1% at Day0 and Day6; cautious megakaryocyte-like fractions are approximately 7.5% and 17.0%. Additional megakaryocyte-associated clusters remain Unknown in this run's presentation.

The expanded panel distinguishes basophil-, eosinophil- and mast-associated programs. Clusters 23 and 25 contain 1,306 basophil-like candidates, all Day6. These remain transcriptional candidates, not validated mature-cell identities. Relative-score proposals lacking matching absolute marker evidence are kept separate from cautious AI revisions. HLF remains unavailable in the Day6 source rather than a measured zero.

![Original independent hESC UMAP](original/hESC/figures/01_independent_umap.png)

## Source report's internal controls

The expanded panel adds cardiac, eosinophil and basophil competitors. The source includes a same-panel control on the new clusters to distinguish grouping effects from panel effects.

| Cohort | Label change: same panel versus joint run | Label change after panel expansion | ARI: independent versus joint-subset partition |
|---|---:|---:|---:|
| FL | 22.2% | 5.2% | 0.477 |
| YS | 28.4% | 3.2% | 0.522 |
| hESC | 32.8% | 12.3% | 0.541 |

These are source-reported internal comparisons, not new comparisons against the manual analysis. They measure change or agreement, not biological accuracy. Independent UMAP locations and cluster IDs are not matched coordinates or identities across cohorts. This run extends AI analysis 1; it is not a blinded independent AI replicate.

## Review and reproducibility limits

The local source validation records disjoint cohorts, matched input checksums, zero cell loss, preserved retained-count hashes and unreviewed labels. Source configurations, structured stage reports, quantitative marker evidence, cell metadata, caution records and reproducibility scripts remain in the user's local directory. They are not published as bulk datasets in this report archive.

No donor-level condition DE, trajectory, abundance-significance test, doublet detection/removal or ambient-RNA correction was performed. No cell-cycle scoring/regression outputs or n_neighbors sweep are documented. Human review, verified donor/capture mapping, cell-cycle policy evidence or exception, parameter-selection provenance and model/prompt provenance remain useful supplements under the current knowledge base. Successful execution is distinct from biological validation.

[Back to study records](../README.md).
