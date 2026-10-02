# Connect the plugin to your assistant

First complete [Installation](INSTALLATION.md). The examples here assume you have
cloned this repository and opened a terminal in its root directory. Each host
uses the same five Skills and Python runner in `plugins/scrna-seq-workbench`.

## Codex

1. Open the repository as a project in the desktop app.
2. The project catalog is `.agents/plugins/marketplace.json`. Restart the app if
   the catalog does not appear in the plugin browser.
3. Select **scRNA-seq Workbench** from `scrna-seq-workbench-marketplace` and install
   or enable it. Start a new chat in the project.

If you also have the Codex CLI, you can register the checkout explicitly:

```text
codex plugin marketplace add .
codex plugin marketplace list
```

Registering a catalog makes the plugin discoverable; use the desktop plugin
browser to install it. After updating your checkout, refresh the local install
and start a new chat. Repository changes may differ from the cached installed copy.

See [OpenAI's packaging guide](https://developers.openai.com/plugins/build/plugins)
for client-specific catalog behavior and managed-account restrictions.

## Claude Code

From a terminal in the checkout, install through the included catalog:

```text
claude plugin marketplace add .
claude plugin install scrna-seq-workbench@scrna-seq-workbench-marketplace
claude
```

In the session, open `/plugin` and check the installed entry. Invoke a Skill with,
for example, `/scrna-seq-workbench:scrna-qc`, followed by your request and file paths.

For a single development session, load the plugin directly instead:

```text
claude --plugin-dir ./plugins/scrna-seq-workbench
```

After updating the repository, update the installed plugin:

```text
claude plugin update scrna-seq-workbench@scrna-seq-workbench-marketplace
```

See [Claude's publishing and installation instructions](https://code.claude.com/docs/en/plugins/publish).

## DeepSeek Harness

1. Open the cloned **repository root** as the Harness project. It should contain
   `.git`, `.dsh`, `plugins` and `README.md`.
2. Enable the filesystem skill provider, skill registry/tool and file/terminal
   access in your Harness installation.
3. Start a new session and check that the five `.dsh/skills` entries are listed.
4. Give Harness your Python environment path and the request below.

Harness uses the generated project Skills under `.dsh/skills`; its provider
resolves project scope from the nearest Git root. Keeping this checkout as the
project also keeps the resource paths intact. A GitHub ZIP download has no Git
root; use `git clone` for this setup. To work from a different project, configure
the provider's `customSkillDirs` to include the full absolute path to
`plugins/scrna-seq-workbench/skills`. Keep the rest of the bundle in place.

These are filesystem Skills. See the
[Harness provider documentation](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md)
for the settings supported by your installed release.

## Check the connection

Send this request after following the synthetic-data step in [Quickstart](QUICKSTART.md):

> Use scrna-qc to inspect work/demo/raw.h5ad with work/demo/qc.json.
> The species is human. Save the inspection to work/agent-inspection-01.
> Use the Python environment I supplied during installation.
> Run inspect-only and explain the QC measurements and proposed thresholds.

You should see the assistant load `scrna-qc`, resolve its scripts, run the command
and explain `cell_qc.csv`, `threshold_suggestions.json` and `report.json`.
Inspection produces no `filtered.h5ad`; filtering is a separate step.

If it only describes a plan, ask it to execute the inspection. If it cannot run
commands, check the host's file and terminal permissions. If it cannot find the
Skill, check the installed entry and restart the session. A package validator
checks files; this conversation checks whether your host can use them.

For a reproducible host acceptance record, save the host version, request,
execution trace, output paths and any errors. Completed host acceptance records
are separate from the repository's Python tests.
