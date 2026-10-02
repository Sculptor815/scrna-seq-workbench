# Development and publication

## Layout

```text
plugins/scrna-seq-workbench/  canonical five Skills, references, assets and Python
.agents/plugins/            Codex marketplace
.claude-plugin/             Claude Code marketplace
.dsh/skills/                generated DeepSeek Harness project entries
examples/                   small synthetic-data generator
scripts/                    checks, adapter generation and release packaging
tests/                      numerical/data-contract tests
docs/                       setup, validation and this guide
```

Edit canonical Skills, not generated Harness entries. Then run:

```text
python scripts/sync_adapters.py
python scripts/validate_package.py
python -m unittest discover -s tests -v
```

Keep numerical behavior changes separate from packaging changes. Add a focused test
when correcting a real numerical or data-contract bug. Review host behavior with the
acceptance prompt in HOSTS. Do not update old benchmark results after tuning.

## Upload to GitHub

Create a new empty repository on GitHub. From this repository directory:

```text
git init
git add .
git diff --cached --stat
git commit -m "Initial research preview"
git branch -M main
```

Then add your real repository URL as `origin` and push `main`. The URL and account
are intentionally not embedded. Review staged files before pushing; the source
package contains no count matrices, trained models, credentials or private reports.
GitHub publication has not been performed by this release-preparation task.

Update the three plugin manifests, Claude marketplace version and README together
when releasing. Regenerate adapters and run the checks. Build a new source ZIP:

```text
python scripts/build_release.py --output ../scrna-seq-workbench-source.zip
python scripts/build_release.py --format plugin --output ../scrna-seq-workbench-plugin.zip
```

The builder refuses to overwrite an existing ZIP. It includes hidden host adapters
and excludes local data, environments, caches and Git history. The accompanying
SHA256 file identifies the archive. GitHub Actions runs structural and core checks;
it is provided as configuration, not claimed as executed before publication.

The repository archive includes documentation, benchmark figures, both marketplace
catalogs and DeepSeek project entries. The standalone plugin archive has a single
plugin directory with its manifest directly inside it, suitable for plugin-package
consumers. Use the repository checkout for DeepSeek Harness project discovery.

## Small next milestones

1. Record one successful real host conversation per supported host.
2. Improve per-sample QC evidence and low-RNA population review.
3. Improve marker coverage and conflicting-label handling.
4. Compare changes on development studies, then evaluate on unseen studies.

Avoid expanding into a universal atlas or adding automatic reference downloads
before a first user can complete a well-explained analysis.
