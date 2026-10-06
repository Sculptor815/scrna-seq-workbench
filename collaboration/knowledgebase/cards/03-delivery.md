---
card_id: scrna-kb-03-delivery
version: 0.1.0
status: draft
plugin_version: 0.3.0
scientific_reviewer: null
reviewed_on: null
production_rag_eligible: false
---

# Review sequencing delivery without confusing it with cell QC

Learning draft. Code behavior is tied to the source snapshot below; scientific review is pending.

## Principle

Sequencing quality, mapping quality and cell quality describe different parts of the measurement process. A high sequencing-quality percentage cannot establish that a captured cell is intact, that a sample is correctly labeled or that the study design supports the biological claim.

Definitions and denominators matter. Reads per cell, UMIs per cell and genes per cell are different quantities. Mean and median are not interchangeable. A percentage is interpretable only with its population and definition.

## Decision sequence

1. Identify the sample and source report version. Keep the source file unchanged.
2. Transcribe only metrics actually present, with units and the precise supporting source location.
3. Confirm whether each quantity refers to reads, molecules, called cells or all barcodes. Keep missing values missing.
4. Compare sample-level patterns and flag unexpected discrepancies for investigation. Do not impose a universal pass threshold without assay-specific context.
5. Request the count matrix and cell/sample metadata before numerical cell QC or expression analysis.

## Actual plugin behavior

The `report` command consumes a prepared metrics JSON plus source material. It can inspect visible text from supported documents, but does not provide a universal vendor parser or OCR. The assistant must verify transcribed metrics against the report. Read `review.md` and `report.json`; check that units and evidence survived transcription and that missing fields are explicit.

The synthetic report in the first-run exercise is fabricated test data. It checks file handling, not a sequencing facility's performance. A completed report-review stage is a delivery review, not a certificate of biological quality.

## Self-check

**Question:** Can a vendor report's median genes per cell be used as the mean for a cross-sample comparison?

**Suggested answer:** No. They summarize different aspects of a distribution. Preserve the reported statistic and obtain comparable definitions before combining samples.

## Implementation sources

- [plugins/scrna-seq-workbench/scripts/scrna_core/report_review.py](https://github.com/Sculptor815/scrna-seq-workbench/blob/614917a5c0f678f0894acd3a3a1aa5f9542523de/plugins/scrna-seq-workbench/scripts/scrna_core/report_review.py)

[Learning path](../LEARNING_PATH.md) | [Review worksheet](../REVIEW_WORKSHEET.csv)
