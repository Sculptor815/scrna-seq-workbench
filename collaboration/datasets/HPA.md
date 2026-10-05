# Human Protein Atlas source notes

The Human Protein Atlas (HPA) provides a tissue-organized entry point to published
single-cell studies. Cite both HPA and the original study when using an export.

- [Single-cell source studies](https://www.proteinatlas.org/humanproteome/single%2Bcell/single%2Bcell%2Btype/data)
- [Single-cell methods](https://www.proteinatlas.org/humanproteome/single%2Bcell/single%2Bcell%2Btype/method)
- [Download page](https://www.proteinatlas.org/about/download)
- [Per-gene, per-cell read-count archive](https://www.proteinatlas.org/download/tsv/rna_single_cell_read_count.zip)
- [License and citation](https://www.proteinatlas.org/about/licence)
- Karlsson et al. (2021), *A single-cell type transcriptomics map of human tissues*:
  [10.1126/sciadv.abh2169](https://doi.org/10.1126/sciadv.abh2169).

## Choose the right data product

| Product | Intended use here |
|---|---|
| Per-cell read-count matrix | Candidate input after verifying values, gene IDs and provenance |
| Per-cell cluster / embedding metadata | Reference material; separate from blinded annotation inputs |
| Aggregated expression such as nCPM | Marker reference or descriptive context; not a raw UMI count matrix |
| Original GEO study | Obtain the original sample design and files when the HPA export lacks them |

The inspected liver export contains `read_count.tsv` (gene rows, cell columns)
and `cell_data.tsv` (cell IDs, clusters and UMAP coordinates). It does not contain
a donor or condition column. Integer-valued counts do not establish that an
export is untouched Cell Ranger output or that it includes all original droplets.

## Reproduce the liver download

1. Download the HPA read-count archive above; it was 3,242,802,912 bytes on
   2026-10-05. Allow enough disk space for the archive and extracted files.
2. Extract only `liver/read_count.tsv` and `liver/cell_data.tsv` into a new local
   source folder. Preserve these files unchanged.
3. Compare their uncompressed sizes and SHA-256 hashes with the
   [manifest](provenance/GSE115469-hpa-v25.1.json). On Windows use
   `Get-FileHash -Algorithm SHA256`; on Linux use `sha256sum`.
4. If the hashes differ, record a new source version and review it before using
   it as the same input. The live download URL is not version-pinned.
5. A 10x-compatible conversion must preserve values and identifiers, record gene
   symbol mapping and verify a read-back comparison. The conversion is pending
   in the recorded snapshot; no prepared 10x files are included in this repository.

The local preparation downloaded only the liver ZIP members using HTTP ranges
and verified their archive CRCs. Downloading the full archive and extracting
those members should yield the same uncompressed files for that source version.

The download page identified HPA v25.1 at retrieval. HPA's license page specifies
CC BY 4.0 for copyrightable database content and notes third-party constraints;
check the original study's terms for the intended use. This folder stores links
and provenance, not redistributed expression matrices or paper PDFs.
