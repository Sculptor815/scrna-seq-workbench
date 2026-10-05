# Dataset shortlist

Start with **GSE115469 (human liver)**. The other three studies are proposals for
joint selection. All four are linked from the [HPA single-cell source table](https://www.proteinatlas.org/humanproteome/single%2Bcell/single%2Bcell%2Btype/data).

| Study | Tissue | HPA-export cells | Potential use in the agent | Current status |
|---|---|---:|---|---|
| [GSE115469](studies/GSE115469.md) | Liver | 6,404 | Intake, QC audit, cell annotation and macrophage expression questions | Selected for initial local preparation; files checked; analysis/review pending |
| [GSE116222](studies/GSE116222.md) | Colon epithelium | 7,339 | Epithelial identity and barrier biology; original study also has ulcerative colitis samples | Proposed; source metadata checked; matrices not downloaded |
| [GSE137537](studies/GSE137537.md) | Retina | 7,222 | Neural cell annotation and regional expression questions | Proposed; source metadata checked; matrices not downloaded |
| [GSE130973](studies/GSE130973.md) | Skin | 15,579 | Fibroblast annotation and feasibility of donor-level aging analysis | Proposed; source metadata checked; matrices not downloaded |

Cell counts above describe the **HPA tissue exports**, not the total cells or
conditions in each original study. HPA and GEO copies are not interchangeable.
The HPA atlas subset must not be assumed to contain the disease, age or regional
comparisons described by the corresponding paper.

## Open and edit

- [HPA source and download notes](HPA.md)
- [Machine-readable study catalog](catalog.json)
- [Liver download and validation manifest](provenance/GSE115469-hpa-v25.1.json)
- [Template for another study](templates/STUDY.md)
- [Collaboration process](../README.md) and [decision log](../DECISIONS.md)

Each study card contains paper links, public download locations, a proposed
question and the checks needed before using its matrix. Review the card rather
than treating a GSE accession as proof of analysis readiness.

## Selection criteria

Prefer a clear biological question, accessible numerical inputs, documented
count units, traceable sample/donor metadata and an analysis that fits the local
runner. Confirm tissue and species, available gene identifiers, source labels,
and whether preprocessing already removed relevant cells or genes.

For condition comparisons, establish biological donors and experimental design
before running pseudobulk DE. A large cell count cannot replace independent
donors. For annotation testing, hold published labels and embeddings separately
from the agent's input; use a documented, tissue-matched marker panel and record
human review. When a question exceeds current tools, mark the missing capability.

These studies are **public development candidates**, not an independent hidden
test set, and no scientific performance scores are claimed here.
