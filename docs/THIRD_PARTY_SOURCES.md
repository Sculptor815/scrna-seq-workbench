# Third-party sources

The MIT license covers this project's original code and documentation. Publications,
externally hosted figures, reference atlases and public datasets retain their own
terms. Original figures are linked from their source websites.

Original studies, figure URLs and representation types are in
[the figure manifest](../benchmarks/original_figures.json). Input locations and exact
download hashes are in [the historical source record](../benchmarks/legacy/sources.json).
[Dataset attribution](../benchmarks/dataset_sources.json) adds a citation, DOI,
distribution source, derivative description and license status for every study.

| Dataset | Publication | Distributed copy |
|---|---|---|
| Kang | Kang et al., 2018, [10.1038/nbt.4042](https://doi.org/10.1038/nbt.4042) | Pertpy processed PBMC copy |
| Haber | Haber et al., 2017, [10.1038/nature24489](https://doi.org/10.1038/nature24489) | Pertpy regions copy |
| Paul | Paul et al., 2015, [10.1016/j.cell.2015.11.013](https://doi.org/10.1016/j.cell.2015.11.013) | Scanpy HDF5 copy |
| Zeisel | Zeisel et al., 2015, [10.1126/science.aaa1934](https://doi.org/10.1126/science.aaa1934) | scvi-tools distribution of the author expression table |
| Baron | Baron et al., 2016, [10.1016/j.cels.2016.08.011](https://doi.org/10.1016/j.cels.2016.08.011) | GEO GSE84133 human samples |

A dataset-specific redistribution license has not been verified for these exact
downloaded copies. Their records therefore use `license.identifier: null` and
`status: not_verified`. The software license of a download client and the license
of a paper do not establish the license of the dataset it distributes. This
record provides attribution and an explicit remaining check, not license clearance.

The repository includes derived UMAP coordinates, neutral cell IDs, reference
labels, marker summaries and evaluation tables. Count matrices are external.
The Haber table with original IDs from the older local package is not included.
Retain the study citations, download sources and transformation record with any
derived results, and check applicable source terms before further redistribution.

Method sources: [HPA](HPA_METHODS.md), [Scanpy](https://scanpy.readthedocs.io/), [scvi-tools](https://docs.scvi-tools.org/), [PyDESeq2](https://pydeseq2.readthedocs.io/). Client packaging sources are in [HOSTS.md](HOSTS.md). The project is independent and is not endorsed by these organizations.
