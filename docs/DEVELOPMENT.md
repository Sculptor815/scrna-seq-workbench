# Development and releases

The published repository is
[Sculptor815/scrna-seq-workbench](https://github.com/Sculptor815/scrna-seq-workbench).
Work on a checkout of this repository and keep analysis data in ignored local
folders or a separate study directory.

## Layout

```text
plugins/scrna-seq-workbench/  six canonical Skills and Python runner
.agents/plugins/            Codex marketplace
.claude-plugin/             Claude Code marketplace
.dsh/skills/                generated Harness project entries
examples/                   synthetic-data generator
scripts/                    validation, verification and packaging
tests/                      regression tests
benchmarks/                 historical results, evidence and frozen source
docs/                       user tutorials and evaluation notes
```

Edit canonical Skills and regenerate the Harness entries. Run checks from the
repository root with the environment described in [Installation](INSTALLATION.md):

```text
python scripts/sync_adapters.py
python scripts/validate_package.py
python scripts/verify_benchmark.py
python -m unittest discover -s tests -v
```

Test numerical changes with a relevant regression case. The benchmark verifier
needs only Python's standard library. Model fitting and the synthetic workflow
need their scientific dependencies. For host behavior, run the acceptance session
in [Host setup](HOSTS.md) and retain the execution record.

## Historical benchmark records

Treat `benchmarks/legacy`, `benchmarks/evidence` and the frozen ZIP as historical
records. New experiments go to a new directory. Verification reads the committed
hash manifest; it has no option to replace expected hashes. Intentional evidence
changes need a reviewed explanation and a new benchmark identity, rather than
silently changing the old scores. See [benchmark verification](../benchmarks/README.md).

## Prepare a release

Update the three plugin manifests, Claude marketplace entry, README, CITATION.cff
and RELEASE_NOTES.md to the same version. Add a changelog entry, regenerate the
adapters and run the checks above. Package validation also checks relative Markdown
and HTML image links, including the comparison tables.

Build both archive formats in a local work directory:

```text
python scripts/build_release.py --format repository --output work/scrna-seq-workbench-v0.3.0-repository.zip
python scripts/build_release.py --format plugin --output work/scrna-seq-workbench-v0.3.0-plugin.zip
```

| Archive | Contents | Use |
|---|---|---|
| Repository | Tutorials, tests, benchmark records and source ZIP, both catalogs and Harness entries | Source distribution and development |
| Plugin | One plugin root with six Skills, scripts, references and requirements | Host plugin installation |

The builder runs package and benchmark verification first, checks archived
versions and writes an adjacent `.zip.sha256`. Existing archives are refused.
Local data, caches, environments and Git history are excluded. The only included
ZIP is the explicitly pinned historical source archive.

## Publish an update

Review `git status` and the diff, commit the intended source changes, then push to
the existing `origin`. Check the commit's
[Actions run](https://github.com/Sculptor815/scrna-seq-workbench/actions) for both
Windows and Linux. The workflow runs tests and verification; it does not publish
releases automatically.

A GitHub Release is a separate action. When publishing one, use a tag matching the
validated version and attach the two newly built archives and their checksum
files. Describe the plugin archive and full repository archive separately.
An old ZIP with a different version is not a substitute for either artifact.
Public plugin-directory submission is also separate from a GitHub push.

## Branch roles

`main` publishes the analysis plugin. `benchmark` adds developer research evaluation
and review records/templates. Merge analysis updates from main into benchmark;
keep evaluation-specific commits off main. The scoring runner is not registered
as a Skill or an analysis command. Historical frozen benchmark records remain on
main for release provenance and regression verification; they are not an active
user-facing scoring module.
