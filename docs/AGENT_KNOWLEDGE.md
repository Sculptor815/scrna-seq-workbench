# How the agent receives the knowledge base

The plugin ships its analysis policy as ordinary local Markdown. No database,
embedding service or extra connector is needed.

1. Each of the six canonical Skills tells the agent to read the local
   [policy entry point](../plugins/scrna-seq-workbench/references/agent-policy.md).
2. That entry point specifies the relevant sections of the bundled
   [knowledge base](../plugins/scrna-seq-workbench/references/knowledgebase.md)
   for the current stage, plus the shared mandatory rules.
3. The runner enforces the selected backend and cell-cycle input contracts and records the policy
   file hash in report.json. This records policy provenance; it cannot prove that
   an agent read the instructions or that biological decisions were human-reviewed.

## Maintaining one source

Edit [collaboration/knowledgebase/README.md](../collaboration/knowledgebase/README.md).
Do not hand-edit the bundled copy or generated DeepSeek adapters. Run:

```text
python scripts/sync_knowledgebase.py
python scripts/sync_adapters.py
python scripts/validate_package.py
```

The synchronizer rewrites relative resource links so they work inside a standalone
plugin ZIP. Validation rejects stale knowledge copies or a Skill missing the entry
point. The archive builder verifies that the policy and cycle-gene assets are included.
New policies that require computational changes still need runner changes and tests;
Markdown is not an executable configuration.

## Using an update

Update the checkout/plugin through the normal host installation mechanism, refresh
the installed plugin and start a fresh session if required by the host. Previously
installed ZIPs/caches do not receive new files just because GitHub changed.
Tell the agent which checkout and Python interpreter to use. A useful request is:

> Use this updated scRNA-seq Workbench. Read its bundled agent-policy.md and the
> relevant knowledge-base sections first. Establish dataset relationships, use
> default scVI with cell-cycle covariates, explain runtime/hardware choices and
> the explicit Harmony alternative, show neighbor/resolution
> candidates for my choice, and preserve annotation uncertainty for my review.

Install requirements-scvi.txt for scVI or requirements-harmony.txt for explicitly
selected Harmony. Before a full run, disclose that it may exceed 1 hour. Missing
a GPU is compatible with CPU scVI; it is not permission to switch automatically.
Harmony requires verified technical batches and separate cycle regression. The knowledge base travels with both source
checkouts and standalone plugin archives across the supported hosts. Actual host
loading still requires a host acceptance check; repository checks alone cannot
establish it.
