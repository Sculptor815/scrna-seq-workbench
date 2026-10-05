# Collaboration workspace

Use this folder to select real studies, agree on biological questions and record
what the local scRNA-seq agent needs to do. Start with the
[dataset shortlist](datasets/README.md).

## Working together

1. Pick a GSE accession from the shortlist, or propose another study using the
   [study card template](datasets/templates/STUDY.md).
2. Add the biological question, relevant figure or Methods section, required
   files and a proposed analysis. Record what would count as useful evidence.
3. Discuss changes in a pull request. The researcher reviews scientific scope;
   the engineering review checks inputs, execution and reproducibility. Add
   names and dates only when those reviews have happened.
4. Update the study card and [catalog](datasets/catalog.json) together. Summarize
   agreed changes in the [decision log](DECISIONS.md).

Collaborators with write access can edit on a branch and open a pull request;
others can fork the repository and propose changes. This folder does not change
repository access permissions.

Keep count matrices, downloaded papers and analysis outputs in a local study
folder. Commit source links, file manifests, preparation instructions and review
notes here. `local/` is ignored if a local download location is needed within
this folder. The project's [third-party source policy](../docs/THIRD_PARTY_SOURCES.md)
also applies.

These public study cards are development material. Hidden evaluation answers,
scientific rewards and private test decisions belong outside the agent-visible
product; evaluation development remains on the `benchmark` branch.
