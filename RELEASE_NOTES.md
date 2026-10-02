# v0.2.1 - installation guide and benchmark verification

This update provides step-by-step installation for Windows/D:, Linux and macOS,
host setup for Codex, Claude Code and DeepSeek Harness, and a walkthrough from
vendor reports to reviewed annotations and donor-level DE.

The benchmark now includes the original v0.1.0 source ZIP, matched against all
37 historical file hashes, plus a read-only verifier used in Windows/Linux CI.
It checks artifact hashes, stage dimensions and seed-0 annotation agreement and
coverage. Input and post-QC gene counts are documented separately. Historical
scores and pending annotation decisions are unchanged.

Rendering and evidence regeneration require fresh output locations outside the
committed records. Packaging checks versions and includes the frozen archive
in the full repository ZIP. Dataset attribution now records each study's DOI,
source and explicitly unverified redistribution-license status.

Mitochondrial QC summaries now provide only an upper suggested bound. The change
does not alter applied filters. Generated vendor review Markdown is in English.

See [validation](docs/VALIDATION.md) for test evidence and remaining limitations,
and [the review response](docs/REVIEW_FIXES.md) for the issue-by-issue resolution.
