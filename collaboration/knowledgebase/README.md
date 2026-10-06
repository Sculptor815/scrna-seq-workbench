# Analysis knowledge base: authoring workspace

This is the place to write analysis experience for the future scRNA-seq agent.
It now includes twelve learning cards, authoring templates and a draft example, not a running RAG service.
No document here is automatically added to an agent's production knowledge.

Start with the [experience template](templates/EXPERIENCE.md), the
[source manifest template](templates/SOURCES.csv), and the
[draft donor-design example](examples/donor-design.md).
See the [agent development plan](../AGENT_DEVELOPMENT.md) for integration.

## Learn with the existing plugin

Start with the [v0.1.0 learning path](LEARNING_PATH.md) and
[guided 400-cell exercise](FIRST_RUN.md). Each card explains principles, decision
steps, actual tool behavior and a self-check. Record your scientific corrections
in the [review worksheet](REVIEW_WORKSHEET.csv). All cards remain drafts.

## What to write first

Write one decision or recurring problem per card. The first five useful topics
are clarifying a biological question, identifying usable counts, choosing
sample-aware QC, reviewing cell identity, and checking donor-level comparisons.
Write the rationale and conditions you actually use rather than an idealized
pipeline. Include failures and counterexamples, not only successful analyses.

A useful card answers:

1. When does this advice apply, and when does it not apply?
2. What evidence must be inspected before acting?
3. What action or parameter choice follows from that evidence?
4. What observable result would support or contradict the decision?
5. What should happen if the analysis fails or remains ambiguous?
6. Which source, figure, Methods section, software version or reviewed case
   supports the recommendation?

Fixed numeric settings need a source and a matching experimental context. Where
calibration is required, describe how to choose a range and judge the results;
do not invent a universal cutoff. Keep units and any prerequisite conditions
next to the values when writing the note.

## Review and provenance

Use stable card IDs and explicit versions. A draft is not human-reviewed. Record
reviewer, date, scope and unresolved issues before marking a version reviewed.
Distinguish personal experience, published evidence, official software behavior
and a project-specific decision. Record disagreements rather than merging them
into a false consensus. Human approval is recorded by the reviewer, not the agent.

Public Markdown is English, following the repository convention. The owner can
supply rough notes in Chinese; an English translation should be checked for
scientific fidelity before it is marked reviewed. Do not put private patient
information or unpublished confidential findings into public draft notes.

## File placement

- Copy the experience template into a new Markdown file under `cards/` when
  contributing an actual card; use a descriptive filename and stable ID.
- Record source identifiers in a project source manifest based on the CSV
  template. Leave unknown hashes or dates blank rather than guessing.
- Keep permitted local full-text PDFs and private notes outside Git, for example
  in the ignored `collaboration/local/` folder or a separate study directory.
- Commit your original notes, source links, bibliographic information and review
  decisions. External papers and datasets retain their own terms.
- Do not add credentials, index caches, hidden answers or scientific rewards.

## Planned retrieval behavior

The future index will preserve source locations, card versions and review state.
It will filter for applicability and retrieve complete decision context, including
exceptions and failure handling. Exact gene/accession names should remain
searchable. Retrieved documents cannot authorize software installation, arbitrary
code execution or changes to project rules.

A separate reviewer mode may inspect draft cards. Default user analysis will use
reviewed versions. The current repository has no automatic index builder or
runtime enforcement of this policy yet; implementation and tests are tracked
in the development plan.

## Review external analysis experience

The [first external evidence collection](evidence-review/2026-10-06/README.md)
contains 18 candidate decisions from 21 official, method-author and community
sources. Read the source observations, limitations and review questions before
promoting any advice. All entries await owner review; analysis code is unchanged.
