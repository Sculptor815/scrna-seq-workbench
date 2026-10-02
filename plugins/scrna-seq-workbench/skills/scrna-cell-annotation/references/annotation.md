# Annotation and review

A marker panel declares species, tissue, source and genes per type. The included
PBMC panel is only a broad-lineage demonstration. For tumors, cell lines, nuclei
or other tissues, supply a matching panel and include plausible alternatives.
Cell lines may have abnormal programs; forcing them into normal tissue atlas
labels is not valid by default.

HPA input is a local TSV with Gene name, Cell type, nCPM. Declare an explicit
allowed-types JSON for the tissue and a source/rationale. Keep a pinned reference
release and original download URL alongside the file; runtime hashes the data.
HPA column versions differ. The code rejects mismatched schemas instead of
assuming nTPM and nCPM are interchangeable. No HPA data is bundled or downloaded
automatically by this release.

The heuristic scores markers by z-scored cluster mean log-normalized expression.
It is relative to the other clusters and may change with clustering resolution.
Require marker coverage and at least two comparable candidate types; constant
markers and single-cluster cases produce Unknown, not infinite confidence.
HPA's own reliability is not the probability that a new query label is correct.

The coverage gate uses informative markers (finite across-cluster z scores),
not just genes present in the matrix. Both fractions are exported. At least two
informative markers are required. HPA marker selection requires nCPM >= 1 and
positive specificity versus the allowed alternatives; it is still heuristic.
Surrounding whitespace in reviewed cell-type labels is trimmed before grouping.

Review annotation_evidence.csv and exploratory_markers.csv alongside UMAPs and
sample distributions. Consider positive, negative and missing markers. Tissue-
specific names such as Kupffer cells should not be accepted for blood merely
because macrophage markers overlap. Use a broad supported label or Unknown.

Review table: cluster,cell_type,reviewer,rationale. Every cluster appears once.
Only a genuine reviewer decision should populate it. Changing cluster resolution
invalidates prior review mappings; start a new review. Cluster marker p-values
reuse the discovery data and are exploratory. Do not use the same marker panel
as both algorithm and sole benchmark ground truth.

Source: https://www.proteinatlas.org/humanproteome/single+cell/single+cell+type/data

The default policy is now [HPA-guided evidence and manual review](../../../references/hpa-guided-annotation.md). The older four-column reviewed-label template requires explicit `--annotation-policy legacy`.
