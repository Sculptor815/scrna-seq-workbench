# Vendor report interpretation

1. Identify report software/assay/version and specimen; MGI DNBelab is not 10x.
2. Separate sample-level sequencing metrics from per-cell biology/QC.
3. Preserve each metric's definition, denominator and source location. Compare
   only equivalent metrics across vendors and versions.
4. Inventory count matrices, feature/barcode files, cell calls, sample/capture
   mapping, organism/reference build, and donor/condition metadata.

| Metric | Useful interpretation | Does not establish |
|---|---|---|
| Estimated cells | Vendor-called barcodes/cells; compare with intended loading and matrix dimensions | Number of high-quality singlets after QC |
| Median UMI/cell | Typical detected molecule count | Sequencing reads or universal sample quality |
| Median genes/cell | Typical detected gene complexity | Tissue-independent quality threshold |
| Mean reads/cell | Average depth on the vendor-defined cell denominator | Median UMI or effective unique molecules |
| Saturation | Duplicate/novel molecule behavior under this assay | A universal resequencing decision alone |
| Reads in cells, mapping, Q30 | Library/sequencing/reference context | Per-cell mitochondrial fraction or doublet rate |
| Barcode rank curve | Cell calling separation and ambient signal context | An automatic correct threshold from a screenshot |
| Beads per droplet | Vendor bead/cell reconstruction metric | Fraction of cell doublets |

For screenshots, say which visible panel was checked. Missing panels remain
missing, even if a typical vendor report usually includes those values. The
numeric validator records verified transcription; it does not independently OCR
images or guarantee that a copied value matches pixels. Use original HTML/PDF
and vendor metric definitions when ambiguity affects interpretation. The HTML
helper extracts static text only and never executes report JavaScript.

The plugin's first skill is delivery review, not a FASTQ alignment engine.
If matrix files are absent, obtain them or design a separate assay-specific
preprocessing job. BCL demultiplexing, 10x count/multi and MGI vendor workflows
are not interchangeable. Never suggest running Cell Ranger on DNBelab by default.
