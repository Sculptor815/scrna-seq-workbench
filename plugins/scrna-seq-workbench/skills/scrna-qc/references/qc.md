# QC decisions

Inspect metrics by sample before deciding thresholds. The default example has
minimum 200 genes and 1 UMI; upper mitochondrial/hemoglobin/UMI fences are unset.
It is a demonstration starting point, not a universal profile. Use per_sample
overrides to reflect tissue, nuclei versus cells, chemistry and dissociation.

Lower limits are inclusive; upper limits are exclusive. Quantile upper limits
are computed independently in each sample on prefilter cells. Tied values at an
upper threshold are removed; quantiles therefore need not remove exactly the
nominal fraction. Raw-matrix metrics are retained consistently across filters.
The first exclusion reason per cell is recorded; reason totals sum to total loss.
Gene filtering occurs after cell filtering and is recorded separately.

MT/RP/HB patterns assume gene symbols and the declared species. Ensembl IDs need
a versioned mapping. Missing MT/HB symbols plus the corresponding enabled filter is an error,
not evidence of perfect mitochondrial QC. High mt/HB/UMI can reflect biology;
do not remove a lineage simply to make distributions look cleaner.

Scrublet uses raw counts from each physical capture after basic cell QC. Pass
the actual capture key and expected doublet rate. An intended doublet analysis
that cannot run fails explicitly; it is not silently skipped. Do not treat a
high-count quantile fence as a substitute for doublet scoring. Scores are model
outputs, not truth. Cell calling and ambient-RNA removal are separate problems;
this release does not implement empty-droplet calling or ambient correction.

When a metric has zero MAD, suggested limits are null and the suggestion is
marked degenerate_mad. Never copy a zero-width range into an exclusive upper
filter. Missing ribosomal symbols also produce a warning.

Source: https://scanpy.readthedocs.io/en/stable/tutorials/basics/clustering.html
