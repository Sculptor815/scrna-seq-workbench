# Select studies for a research question

For each candidate, record a source URL and access date for each checked fact.
Keep unknowns explicit. A dataset can be suitable for expression localization but
unsuitable for a treatment comparison; suitability belongs to a question.

| Check | Evidence to retain | Effect on selection |
|---|---|---|
| Biological fit | Organism, tissue, disease, perturbation, time points, sampling/sorting | Establish the comparison and what is absent |
| Identity and files | Paper DOI, accession, linked data-availability section, exact matrix and metadata files | Inspect counts provenance, license and download size |
| Design | Biological donors per condition, pairing, capture and batch relationships | Distinguish independent replication from cell numbers |
| Processing | Raw/filtered matrix, exclusions, cell labels, gene IDs | Decide whether existing processing can be reused |
| Publication status | Publisher/PubMed notice checks, URLs and dates, unresolved access failures | Describe the scope of any notice; do not infer all findings are false |
| Independent support | Perturbation, histology/protein evidence, independent cohorts or studies | Check shared donors/data and whether the evidence tests the same claim |

No search result does not establish that a paper or dataset is fabricated. A lack
of notices does not establish validity. Orthogonal experiments reported within the
same paper strengthen a claim differently from an independent replication.
For a selected dataset, retain file hashes and processing history in the run.
Do not copy controlled-access or restricted files into a public repository.

Return a compact shortlist with reasons to select, defer or reject, rather than a
long list of loosely related accessions. Download only within the authorized resource
budget. If no candidate supports the requested inference, explain the missing design
and offer a useful narrower analysis.
