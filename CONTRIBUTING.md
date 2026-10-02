# Contributing

Start with an issue describing a concrete analysis failure or a reproducible improvement. Use synthetic or openly licensed public examples; do not attach private count matrices or vendor reports.

Edit canonical Skills under `plugins/scrna-seq-workbench/skills`, run `python scripts/sync_adapters.py`, then structural checks and the relevant tests. Preserve raw counts and report provenance. Document any change to QC, clustering or annotation in CHANGELOG.md. Separate development studies from held-out evaluation.

Do not change historical benchmark scores after tuning. Generate a new protocol/run identifier. Keep all Markdown in English and user-facing explanations in the user's language. See [development](docs/DEVELOPMENT.md) for commands.
