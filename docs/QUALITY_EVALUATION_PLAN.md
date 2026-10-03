# Research quality plan

The product is an analysis assistant: a user brings a biological question and
receives useful, traceable evidence. Developers evaluate completed sessions in
[a separate benchmark module](../benchmarks/research/README.md). The plugin neither
imports that module nor reads its expected answers.

## First research pilot

Build five independent study families around explicit biological questions:
injury/repair cell states, perturbation response, treatment-associated immune
changes, a disease-associated mechanism and a proposed gene-to-cell-type link.
Select studies for design and evidence rather than availability or journal prestige.
Before inclusion, verify counts/metadata, donor design, source linkage, notices,
permissions and orthogonal or independent validation. Keep unchecked candidates
out of the locked test set. Avoid counting related cohorts as independent cases.

Potential starting points for curator screening include the epithelial injury
question in [Strunz et al.](https://doi.org/10.1038/s41467-020-17358-3), and the
macrophage/T-cell circuit question in [Grant et al.](https://doi.org/10.1038/s41586-020-03148-w).
These are literature leads, not certified reliable datasets or completed cases.
Expand beyond lung biology before locking the five-study pilot.

For each study family prepare a natural user request, fixed tool/resource budget,
design and file checks, claim-level evidence, acceptable alternative conclusions,
critical errors and case-specific scoring anchors. Keep developer references in
a private evaluation workspace. Public scientific sources remain available under
the same search conditions for every evaluated release.

## Primary outcomes

Score data suitability (20%), analysis relevance (25%), evidence reasoning (30%),
user usefulness (15%) and interaction efficiency (10%) from documented reviews.
Keep completion, critical errors, time to first useful result, total time, cost
and user interventions visible. Weights are provisional until pilot calibration.
Report failed and incomplete attempts as well as successes.

Credit evidence-supported disagreements and appropriately limited conclusions.
Original-paper agreement is an evidence comparison, not the scoring target.
Where disagreement matters, review data versions, sample inclusion, methods,
uncertainty and independent experiments. Preserve original reviewer records and
adjudication before using the deterministic score calculator.

## Supporting technical checks

QC decisions, low-RNA/rare-population retention, annotation evidence, donor-level
design, representation stability and count provenance explain why a research result
is trustworthy or misleading. They support the question-level assessment. UMAP
appearance or aggregate annotation accuracy cannot stand in for scientific utility.
The existing five-study records remain unchanged and are development/regression
evidence; they are not an unseen test of the new workflow.

## Release acceptance and limits

1. Validate the analysis/evaluation boundary, output provenance and numerical summaries.
2. Run a host conversation from a biological question to a useful saved result.
3. Curate and review five independent study cases, then lock their versions.
4. Run matched baseline/new-plugin sessions and complete independent review.
5. Publish case-level outcomes, errors and uncertainty with the evidence record.

This release implements step 1 and the user workflow. Steps 2-5 remain pending;
software tests do not establish an improvement in biological research performance.
No new scVI training, real-data research benchmark or expert review is claimed.
