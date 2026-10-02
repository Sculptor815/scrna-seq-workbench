# Original publications and plugin comparisons

These panels are for scientific inspection, not proof of equivalence or an HPA accuracy benchmark. Original images below remain hosted by their source. Internet access is required for those images. Two original assets could not be retrieved; their source links and the missing status are explicit.

**Read the axes and provenance:** original t-SNE/heatmaps are not UMAP. Every locally rendered comparison uses the plugin's existing scVI seed-0 UMAP. Its left panel replots author/reference broad labels on our coordinates; it is not an author embedding. The same label uses the same color in reference and proposal panels. Gray means Unknown.

The plugin panels are legacy unreviewed marker proposals. New [HPA-guided packets](../benchmarks/README.md) provide evidence and pending review forms; final HPA-reviewed scores are not available. No seed was selected for visual appeal.

## Kang et al. 2018

[Original publication / figure](https://pmc.ncbi.nlm.nih.gov/articles/PMC5784859/figure/F3/) · DOI: 10.1038/nbt.4042

Figure 3a: t-SNE; PBMC conditions and estimated types. The public processed copy has 24,673 cells; the paper singlet counts total 24,305. Cell-version equivalence is unresolved.

<table><tr><th>Original publication figure (external)</th><th>Our UMAP and labels</th></tr>
<tr><td><a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC5784859/figure/F3/"><img src="https://cdn.ncbi.nlm.nih.gov/pmc/blobs/85ef/5784859/45d5c071fa72/nihms921103f3.jpg" width="420" alt="Original kang publication figure"></a></td><td><a href="figures/kang-comparison.png"><img src="figures/kang-comparison.png" width="750" alt="kang plugin comparison"></a></td></tr></table>

[Marker heatmap](../benchmarks/evidence/kang/marker_heatmap.png) · [Marker measurements](../benchmarks/evidence/kang/marker_expression.csv) · [Pending review form](../benchmarks/evidence/kang/hpa_review.template.csv) · [Per-type scores, legacy](../benchmarks/legacy/kang/scvi_0_annotation_per_type.csv)

## Haber et al. 2017

[Original publication / figure](https://pmc.ncbi.nlm.nih.gov/articles/PMC6022292/figure/F1/) · DOI: 10.1038/nature24489

Figure 1b: t-SNE of 7,216 epithelial cells. The benchmark uses the 9,842-cell regions copy. The paper panel is contextual and is not the same selected cells.

<table><tr><th>Original publication figure (external)</th><th>Our UMAP and labels</th></tr>
<tr><td><a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC6022292/figure/F1/"><img src="https://cdn.ncbi.nlm.nih.gov/pmc/blobs/0fcf/6022292/9681315d11de/nihms910777f1.jpg" width="420" alt="Original haber publication figure"></a></td><td><a href="figures/haber-comparison.png"><img src="figures/haber-comparison.png" width="750" alt="haber plugin comparison"></a></td></tr></table>

[Marker heatmap](../benchmarks/evidence/haber/marker_heatmap.png) · [Marker measurements](../benchmarks/evidence/haber/marker_expression.csv) · [Pending review form](../benchmarks/evidence/haber/hpa_review.template.csv) · [Per-type scores, legacy](../benchmarks/legacy/haber/scvi_0_annotation_per_type.csv)

## Paul et al. 2015

[Original publication / figure](https://doi.org/10.1016/j.cell.2015.11.013) · DOI: 10.1016/j.cell.2015.11.013

Original figure unavailable for verification in this release. Publisher and image service returned HTTP 403. No original UMAP or figure is fabricated. Author-derived labels are compared below.

**Original image status:** publisher figure access blocked; link only. The image below is solely our replot.

![paul plugin comparison](figures/paul-comparison.png)

[Marker heatmap](../benchmarks/evidence/paul/marker_heatmap.png) · [Marker measurements](../benchmarks/evidence/paul/marker_expression.csv) · [Pending review form](../benchmarks/evidence/paul/hpa_review.template.csv) · [Per-type scores, legacy](../benchmarks/legacy/paul/scvi_0_annotation_per_type.csv)

## Zeisel et al. 2015

[Original publication / figure](https://linnarssonlab.org/cortex/) · DOI: 10.1126/science.aaa1934

Author site provides a BackSPIN expression heatmap, not an original UMAP. The author heatmap asset returned HTTP 403. Seven major classes and finer author cluster labels are different annotation levels.

**Original image status:** author heatmap link verified; asset fetch blocked. The image below is solely our replot.

![zeisel plugin comparison](figures/zeisel-comparison.png)

[Marker heatmap](../benchmarks/evidence/zeisel/marker_heatmap.png) · [Marker measurements](../benchmarks/evidence/zeisel/marker_expression.csv) · [Pending review form](../benchmarks/evidence/zeisel/hpa_review.template.csv) · [Per-type scores, legacy](../benchmarks/legacy/zeisel/scvi_0_annotation_per_type.csv)

## Baron et al. 2016

[Original publication / figure](https://pmc.ncbi.nlm.nih.gov/articles/PMC5228327/figure/F1/) · DOI: 10.1016/j.cels.2016.08.011

Figure 1d: human donor 1 t-SNE; other panels show heatmaps and mouse data. The benchmark combines four human donor files (8,569 cells before added QC); this is not the donor-1 paper panel. Paper count differences remain unresolved.

<table><tr><th>Original publication figure (external)</th><th>Our UMAP and labels</th></tr>
<tr><td><a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC5228327/figure/F1/"><img src="https://cdn.ncbi.nlm.nih.gov/pmc/blobs/0c94/5228327/71bab733eb4a/nihms832023f1.jpg" width="420" alt="Original baron publication figure"></a></td><td><a href="figures/baron-comparison.png"><img src="figures/baron-comparison.png" width="750" alt="baron plugin comparison"></a></td></tr></table>

[Marker heatmap](../benchmarks/evidence/baron/marker_heatmap.png) · [Marker measurements](../benchmarks/evidence/baron/marker_expression.csv) · [Pending review form](../benchmarks/evidence/baron/hpa_review.template.csv) · [Per-type scores, legacy](../benchmarks/legacy/baron/scvi_0_annotation_per_type.csv)

## Re-render locally

```text
python scripts/render_comparisons.py
```

This uses the committed public coordinate/label tables. It does not download matrices or train models. Figure provenance and unresolved source access are recorded in [original_figures.json](../benchmarks/original_figures.json).
