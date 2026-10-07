# Shared analysis intake

Read for a new project or entry into an intermediate stage. Reuse existing answers;
collect only information needed for the requested scope. This is a conversational
workflow shared by the research entry point and individual analysis Skills.

Read the [required agent policy](agent-policy.md) and the relevant knowledge-base
sections before choosing stages. Record how datasets form analysis groups from
papers/metadata or user clarification; every new representation requires scVI,
even without batches.

## Ask about facts before technical numbers

Read the supplied files first. Distinguish user statements, verified file evidence
and unknown facts. Group missing information into a short first exchange:

- Goal: the biological question, hypothesis and decision the result should inform. Technical-only tasks can start directly at the relevant stage.
- Data availability: user files or public-study discovery. Missing matrices do not block study selection.
- Sample: species, tissue, cells/nuclei, platform/chemistry and enrichment/sorting.
- Files: raw UMI matrix/format/layer, report if available, metadata and prior filtering,
  normalization or doublet removal. Integer-looking values do not prove provenance.
- Design: actual sample, donor, condition, physical capture and technical batch relationships.
  Complete donor design is required for DE, not every descriptive task.
- Decisions/resources: review a proposed plan or explicitly delegate parameter choice;
  record environment, output location and budget. Never request credentials in a template.

Offer the [intake template](../assets/analysis-intake.template.md), allowing plain-language
answers and unknowns. The [sample-design header](../assets/sample-design.template.csv)
describes experimental combinations. It is not a cell metadata CSV for --metadata.
The latter requires one row per cell with matching cell_id. Pooled captures require
real cell-level demultiplexing; do not assign a donor to all cells in a pooled capture.
See [data contract](data-contract.md). Current numerical support is human/mouse UMI.

## Inspect, propose and record

Use inspect-only for QC before applying filters. If an inspection config is needed,
create one in the run directory and label its values as exploratory, not accepted
filters. Read the relevant sections of [important parameters](important-parameters.md).
Show a compact table: parameter, proposed/user value, evidence, likely impact and status.
Statuses can be unknown, proposed, user-specified, accepted, delegated, or unavailable.

Explain per-sample filters, scVI dimensions, batch-column meaning,
HVGs, neighbors, resolution, seed and training budget as applicable. Disclose any
subsampling: amount, selection method, seed and effect on rare types. A 6000-cell
benchmark cap is not a production default. Report actual values if software caps a setting.

Save an intake record and parameter-decisions.csv with columns:
stage, parameter, requested_value, proposed_value, actual_value, scope, rationale,
evidence, status. Unknown values stay empty. Include paper method branch/location
when available and deviations from it. Never invent an approval record.
Convert chosen values into the actual QC JSON and supported CLI options; these
planning documents are not machine-loaded configurations.

When the user asks to review the plan, finish inspection and present concrete
choices before waiting for acceptance. When they already delegated choices,
continue within that scope and record reasons; do not ask again for every value.
Unresolved experimental facts still need clarification. Plan acceptance does not
approve future cell labels. Revised settings need a new run directory.

## Missing inputs affect specific steps

| Missing/problematic input | Allowed progress | Affected step |
|---|---|---|
| Report only | Interpret report and inventory deliveries | No per-cell QC, training or DE |
| Counts but no vendor report | Inspect matrix with known provenance | Cannot verify sequencing saturation/alignment quality |
| Unknown counts provenance or normalized data only | Locate original counts and processing history | Do not fit a count model or counts DE |
| No matching mitochondrial genes | Check identifiers and other metrics | Mark MT QC unavailable; do not interpret zero as good quality |
| Undefined batch | Clarify or run scVI with batch_key=None and cycle covariates | No arbitrary substitution of condition/donor/sample as batch |
| Complete batch/condition confounding | Describe the design and explore | No claim to separate technical and treatment effects |
| Missing annotation context/reference | Inspect data and request relevant evidence | No universal PBMC panel or forced fine labels |
| Missing donors/insufficient replicates | Descriptive analysis within scope | No donor-level DE; never invent donors |
| Unreviewed label proposals | Inspect candidate evidence | No DE using proposals as final labels |

Keep unavailable evidence, unsupported methods and user-deferred stages distinct.
The CLI does not enforce every experimental fact in this conversational protocol.
