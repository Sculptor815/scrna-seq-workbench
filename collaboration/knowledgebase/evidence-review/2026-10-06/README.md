# External analysis experience: review collection 01

Prepared 2026-10-06. **18 candidate decisions, 21 sources, all pending owner review.** This is a targeted first collection, not a systematic review or a tested replacement workflow. It supplements the twelve existing learning cards without changing them or any analysis command.

## Read and review

1. Use the [review packet](REVIEW_PACKET.md), which separates source observations from our proposed rules, limitations, plugin relevance and a question for the researcher.
2. Record agreement, revisions, disagreement or missing evidence in [OWNER_REVIEW.csv](OWNER_REVIEW.csv). Chinese feedback can be translated for the public cards after scientific checking.
3. After review, promote only a versioned, scoped rule with supporting evidence into the maintained knowledge base. A reply or an issue being closed is not scientific validation.

## What was searched

Targeted searches covered Scanpy/scverse official tutorials and APIs, method-author repositories (SoupX and CellTypist), scvi-tools material, author-maintained Single-cell Best Practices chapters, scverse Discourse and original GitHub issue reports. Queries included sample-specific QC, count-layer warnings, HVG input formats, biological replication and low-expression DE. General forum search results were screened for firsthand, inspectable cases; popularity was not used as evidence of correctness.

Official documentation supports software contracts. Method-author tutorials support the particular demonstrated workflow. Community posts supply debugging observations or candidate practices, with status and context recorded separately. Proposed rules and proposed tests in this packet are our synthesis for review, not claims that the sources tested our plugin.

## Access and reproduction limits

Three records (S05, S07, S16) are explicitly limited to indexed official/article excerpts after direct retrieval failed or was rate-limited. Reread those full sources before approving dependent scientific claims. Other records specify whether a page, issue body, README or directory listing was inspected. No external repository was exhaustively audited and no downloaded notebook was executed.

Live URLs are not immutable versions; `pinned_revision` is null. Access dates and section/post locators are recorded. Before implementation, pin the relevant source revision and test against the installed package version. No full articles or copied tutorial notebooks are redistributed.

## Priorities for owner review

- R02-R06: sample/capture definitions, QC, ambient contamination and matrix provenance.
- R07-R11: representations, HVG inputs, normalization and annotation/integration contracts.
- R12-R15: independent replication, marker ranking, rare-gene filtering and the paired-design concern.
- R16-R18: memory limits, enrichment background and stage-specific gene filters.

R15 explicitly flags a potential methodological problem in a tutorial example; it has not been reproduced. No donor requirement, normalization target or gene filter has been changed to match a web example. SoupX, CellTypist and enrichment remain proposed extensions.

## Index

| ID | Candidate decision | Sources |
|---|---|---|
| R01 | [Use the current tutorial location and record the version](REVIEW_PACKET.md#r01) | S20, S21, S12 |
| R02 | [Inspect QC per sample and revisit exclusions](REVIEW_PACKET.md#r02) | S01 |
| R03 | [Do not transfer a MAD multiplier without its definition](REVIEW_PACKET.md#r03) | S02 |
| R04 | [Define the physical capture before detecting doublets](REVIEW_PACKET.md#r04) | S01, S02 |
| R05 | [Treat ambient RNA correction as a separate, auditable branch](REVIEW_PACKET.md#r05) | S03 |
| R06 | [Validate every component before combining matrices](REVIEW_PACKET.md#r06) | S04 |
| R07 | [A raw slot is not a verified raw-count archive](REVIEW_PACKET.md#r07) | S05, S06, S11 |
| R08 | [Select the HVG input layer to match the method](REVIEW_PACKET.md#r08) | S07, S08 |
| R09 | [Record the normalization target instead of saying only normalized](REVIEW_PACKET.md#r09) | S09 |
| R10 | [Check the classifier input and reference before trusting labels](REVIEW_PACKET.md#r10) | S10 |
| R11 | [Register counts and batch deliberately for scVI](REVIEW_PACKET.md#r11) | S11, S12 |
| R12 | [Do not turn one donor into many biological replicates](REVIEW_PACKET.md#r12) | S14, S16 |
| R13 | [Separate marker ranking from replicated condition DE](REVIEW_PACKET.md#r13) | S15 |
| R14 | [Review low-expression DE instead of importing a forum cutoff](REVIEW_PACKET.md#r14) | S17 |
| R15 | [Review a tutorial design formula against the sampling scheme](REVIEW_PACKET.md#r15) | S13 |
| R16 | [Treat historical memory workarounds as version-specific](REVIEW_PACKET.md#r16) | S18 |
| R17 | [Choose an enrichment background that matches gene eligibility](REVIEW_PACKET.md#r17) | S19 |
| R18 | [Distinguish global gene filtering from test-specific filtering](REVIEW_PACKET.md#r18) | S01, S02, S13 |

Machine-readable files: [items](ITEMS.json), [source records](SOURCES.json). All items remain ineligible for production retrieval. There is no runtime index in this collection.
