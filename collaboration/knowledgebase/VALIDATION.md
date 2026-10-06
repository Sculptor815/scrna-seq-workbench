# Learning-edition validation

Validation date: 2026-10-06. Knowledge base v0.1.0, plugin v0.3.0, implementation snapshot `614917a`.

- Executed all eight PowerShell blocks in [FIRST_RUN.md](FIRST_RUN.md) on Windows with the existing Python 3.12.9 environment. Each exercise used a new output directory.
- The main exercise completed delivery review, inspect-only QC, filtering, PCA/Leiden/UMAP and annotation proposals. The fixture retained 400 cells and 100 genes. Inspect-only produced no filtered matrix; the annotation review template remained pending.
- The optional, separate synthetic execution check completed all six reported stages, including paired donor DE. It uses explicitly labeled artificial truth, not reviewed real-data labels. Its built-in assertions verified count and gene preservation between QC and integration.
- Verified all input and artifact hashes recorded by the eleven stage reports after execution. Checked all twelve catalog entries, pending review states and the pinned source-file hashes.
- Package structure/link checks and historical benchmark verification passed. No analysis code or historical benchmark record was changed.
- No candidate-model or judge API calls were made. scVI training, real-data annotation accuracy, biological validity, production retrieval and human scientific review were not tested by this exercise. Linux execution of this new walkthrough was not performed locally.

The local learning companion and artificial run outputs are kept outside the public repository. These checks establish that the instructions execute in the tested environment; they do not certify the scientific advice. Use [REVIEW_WORKSHEET.csv](REVIEW_WORKSHEET.csv) to record scientific review.
