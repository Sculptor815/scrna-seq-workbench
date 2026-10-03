# Working on scRNA-seq Workbench

Read README.md and docs/DEVELOPMENT.md. Keep the six canonical Skills under
plugins/scrna-seq-workbench/skills; regenerate .dsh entries with scripts/sync_adapters.py.
Do not edit generated adapters by hand. Keep Markdown and UI metadata in English,
but explain analyses in the user's language. Preserve original counts, provenance
and output isolation. No dataset, model, credential or private vendor report belongs
in commits. Run structural checks and relevant tests after changes. Do not claim
host behavior or biological accuracy from package checks alone.
