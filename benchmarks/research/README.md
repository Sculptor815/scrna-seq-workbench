# Research usefulness evaluation (developer tools)

This directory, maintained on the `benchmark` branch, evaluates completed analysis sessions. It is separate from the
installable analysis plugin: no Skill invokes it, and plugin archives exclude it.
Users receive analysis results, provenance and scientific limitations. They do
not need a benchmark configuration or reference answers to run an analysis.

## Unit of evaluation

One case is a realistic biological question and a fixed resource budget. The
assistant must find suitable data, choose analyses and deliver an answer that
helps the user decide what to investigate next. A successful command or a clear
UMAP is not, by itself, a successful case.

Use studies that ask a biological question with an appropriate contrast or
perturbation. Atlases can serve as annotation references. Do not select cases
only because their matrices are easy to download. The historical five-study
benchmark remains a technical regression record, not the main research leaderboard.

Before locking a case, a curator must document the authors' research question,
accession/file linkage, independent biological replicates, processing, publication
notices and available orthogonal/independent evidence. Record retrieval dates.
Case-family splits must keep shared donors and derivative analyses together.
Keep evaluation claims and reviewer records outside the agent's accessible workspace.

## Evidence, not agreement alone

Write the expected evidence as individual claims with source locations, experimental
support and limitations. Do not use an abstract or original annotation as unquestioned
truth. For each claim, reviewers classify the output as supported, partly supported,
contradicted or unresolved. A justified disagreement, narrower conclusion or
insufficient-evidence finding can receive full credit. A correct-sounding conclusion
with an invalid donor design cannot.

When findings differ, review sample/version differences, annotation, normalization,
replicate support, uncertainty and independent experiments. Distinguish independent
replication from multiple publications reusing the same dataset. Missing search
results, an image anomaly or a retraction does not settle every scientific claim.
Resolve disagreements by documented expert adjudication rather than selecting the
result closest to the paper.

## Scoring dimensions

Each dimension receives an integer from 0 to 4, with a rationale and evidence paths.
Weights are provisional and must be calibrated on pilot cases before ranking releases.

| Dimension | Weight | 0 | 2 | 4 |
|---|---:|---|---|---|
| `data_suitability` | 20 | Wrong/unsupported dataset | Related dataset with important unchecked design facts | Verified files and design support the requested inference; limitations and alternatives are clear |
| `analysis_relevance` | 25 | Analysis does not address the question | Useful exploratory outputs, but a major required comparison is missing | Focused, appropriate analyses answer the question or establish precisely why it remains unresolved |
| `evidence_reasoning` | 30 | Fabricated evidence or invalid scientific conclusion | Evidence cited but uncertainty or a competing explanation is poorly addressed | Traceable results, correct inference scope, independent evidence and justified handling of disagreement |
| `user_usefulness` | 15 | User cannot act on the response | Understandable summary with vague next steps | Clear answer, accessible outputs and a specific next decision or experiment |
| `interaction_efficiency` | 10 | No useful progress within budget | Completion with avoidable technical burden | Appropriate initiative, only necessary factual questions and useful results within the agreed budget |

Use 1 for meaningful progress below the 2 anchor and 3 for a mostly complete result
with a material remaining weakness. Add case-specific examples before formal use.
Do not reward verbosity, agreement with the user's hypothesis or fewer questions
when crucial design facts are unknown. Compare efficiency within the same task and
hardware/tool budget. Record time to the first useful result, total wall time,
cost, user interventions and completion status separately from reviewer scores.

Critical errors (fabricated data/citations, invented donors, treating cells as
independent biological replicates, unsupported causal claims central to the answer,
or unavailable claimed outputs) make a session ineligible as a research success.
Preserve its dimension scores for diagnosis. Execution failures remain distinct
from poor scientific answers. A justified conclusion that no suitable data exist
can be a completed case if it fulfills the task's evidence requirements.

## Review and aggregation

Run each case from a clean context with the same user brief, tool availability and
resource constraints. Save answers and artifacts before review. Two reviewers
independently inspect outputs with version/model identity hidden. A difference of
2 or more on any dimension requires adjudication; keep both originals and the
final record. These organizational checks require retained reviewer records; the
calculator does not establish expert independence or scientific truth.

Copy [the record template](review.template.json) into a private results directory.
Complete it only after review. `score.py` validates the final record and computes
its weighted score; it never invokes the agent or assigns scientific ratings.

```text
python benchmarks/research/score.py --record PRIVATE/final-review.json --out PRIVATE/score.json
```

Report all attempted cases, completion rate, eligibility and per-dimension scores.
Do not hide failed cases by publishing only the mean of successful runs. For model
comparisons, use matched cases, report paired differences and bootstrap confidence
intervals by study/case family once enough independent cases exist. Five studies
support a pilot; they are not a broad capability claim.

Current status: protocol and calculator implemented; no new expert-scored research
sessions or formal leaderboard published. See [the quality plan](../../docs/QUALITY_EVALUATION_PLAN.md)
for the first case families and acceptance criteria.

## Keep branches in sync

Install and run user analyses from `main`. Develop evaluation cases and scoring
on `benchmark`. To test a newer analysis version, merge `origin/main` into this
branch and record the analysis commit used for each session. Do not merge this
branch into main just to publish analysis changes. Keep private reviewer identities,
held-out evidence, answers and sensitive inputs outside both public branches.
