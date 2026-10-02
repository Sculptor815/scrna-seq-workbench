# Host setup

All hosts use `plugins/scrna-seq-workbench` as the canonical instruction and code bundle.
The same Python environment is required regardless of the model. Paths below are
relative to this repository's root. Repository layout checks are not live host acceptance tests.

## Codex

The repository contains `.agents/plugins/marketplace.json`, a portable `plugin.json`
and a `.codex-plugin/plugin.json` compatibility manifest.

```text
codex plugin marketplace add .
codex plugin marketplace list
```

In the desktop plugin interface, select `scrna-seq-workbench` from
`scrna-seq-workbench-marketplace` and enable it. Start a conversation with the cloned
repository or your analysis project available and verify that the five skills appear.
After publication, a GitHub repository can be registered instead of the local path.
Client versions and managed policies can affect availability.

Source: [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins).

## Claude Code

For local development:

```text
claude plugin validate ./plugins/scrna-seq-workbench
claude --plugin-dir ./plugins/scrna-seq-workbench
```

Ask Claude to use the Workbench skill by name. If using a marketplace, the root
`.claude-plugin/marketplace.json` points to the same plugin directory. Register this
repository with `/plugin marketplace add .`, then install
`scrna-seq-workbench@scrna-seq-workbench-marketplace` through `/plugin`.
Installing/enabling is a user action; this source package does not modify client settings.

Sources: [Claude plugins](https://code.claude.com/docs/en/plugins),
[manifest reference](https://code.claude.com/docs/en/plugins-reference).

## DeepSeek Harness

Open the **repository root as the Harness project**, not the nested plugin directory.
The committed `.dsh/skills/<name>/SKILL.md` files expose the five workflows through
Harness's filesystem skill provider. They are generated from the canonical Skills
with adjusted resource paths; they use the same scripts, assets and references.

This is a **project-skill integration**, not a Cordis service plugin or an assertion
that Harness reads the Codex/Claude marketplace manifests. The host must have its
skill registry, filesystem provider and skill tool enabled, plus file/shell tools.
Check that all five named skills are visible before starting analysis. Open a fresh
session if your installed release does not refresh the catalog.

Current upstream documentation discovers project skills under `.dsh/skills` and
`.agents/skills`; nested plugin directories are not recursively discovered.
Project scope follows the nearest Git root, so keep this repository as its own
project when using Harness. To use it from another project, add the canonical
`plugins/scrna-seq-workbench/skills` directory through the filesystem provider's
`customSkillDirs` configuration, following your installed version's settings.
Do not copy only a SKILL.md file without its required resources.

Source: [DeepSeek Harness filesystem skills](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md).

## A small acceptance session for any host

First generate the synthetic fixture described in QUICKSTART. In a new session ask:

> Use scrna-qc on work/demo/raw.h5ad. First inspect the data and tell me what is
> missing. Do not filter yet. Treat truth_cell_type as synthetic test metadata,
> not evidence that your annotation method is accurate.

Check observable behavior: the right Skill loads; its resource paths resolve;
the assistant checks counts and sample information; it invokes inspect-only;
the output is new and has the expected report; no filtering is claimed as completed.
Then ask for a proposed analysis plan. Test missing donor information before DE
and missing/unsupported counts separately. Record the host version, prompts,
tool trace, outputs and unresolved questions. An offline manifest check alone
does not establish these behaviors.
