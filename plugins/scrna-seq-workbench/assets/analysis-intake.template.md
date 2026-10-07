# Analysis request and decision record

Answer in chat or fill this file. Use "unknown" where needed; do not provide secrets.
The assistant should reuse existing answers rather than ask again.

## User facts

- Biological question and requested stages:
- Paper/method to reproduce, if any:
- Species and tissue:
- Cells/nuclei, platform/chemistry, enrichment/sorting:
- Matrix path, format and known raw-count location:
- Previous filtering, normalization and doublet processing:
- Vendor report path, or unavailable:
- Sample/cell metadata path:
- Sample, donor, condition, physical capture and technical batch relationships:
- If DE: case/control names, direction and pairing:
- Expected types, desired annotation detail and available references:
- Compute environment, output location and resource budget:

## Decision preference

Choose or describe your preference:
- Inspect first, then let me accept or modify a concrete parameter plan.
- Use my specified values and suggest the remaining choices.
- Choose technical settings within my delegated scope and record the reasons.

Specified values or delegated scope:

## Assistant record

- Verified inputs and counts provenance:
- Missing information and affected steps:
- Actual metadata fields and meanings:
- QC inspection results and per-sample proposed filters:
- Evidence, paper-method branch and deviations:
- Required scVI latent dimensions and any auxiliary PCA diagnostics:
- Batch correction choice and confounding:
- HVGs, neighbors, resolution, seeds, device and training cap:
- Subsampling method, count, seed and limitations, if any:
- Annotation reference, marker coverage gaps and review:
- DE design, independent donor counts and supported-model limitations:
- Decision CSV, commands and actual stage reports:
- New output directories:
- User acceptance/delegation evidence; never prefill agreement:
- Subsequent changes and reasons:

This is a human-readable record, not a config automatically loaded by Python.
