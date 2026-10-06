---
card_id: scrna-kb-11-knowledge
version: 0.1.0
status: draft
plugin_version: 0.3.0
scientific_reviewer: null
reviewed_on: null
production_rag_eligible: false
---

# Turn experience into retrievable decision knowledge

Learning draft. Scientific review is pending.

## Principle

A knowledge base is a maintained collection of statements with context and evidence. A Skill explains how an assistant should perform a task; a tool implements an allowed operation. Retrieval-augmented generation (RAG) retrieves relevant knowledge and gives it to a model during answering. It does not train the model's weights or make the retrieved content automatically correct.

## Authoring sequence

1. Pick one recurring decision from an actual analysis. Write the trigger, prerequisites and scope: species, tissue, assay and analysis stage.
2. Explain the mechanism or statistical principle behind the decision. Separate software defaults from recommendations and your observations from published evidence.
3. Describe an action, observable checks, failure cases and when to ask a researcher. Put units and calibration methods beside numeric settings.
4. Attach source locations and versions. A paper's Methods can support a procedure; a real counterexample can constrain its applicability.
5. Test the card against a normal case and an exception. Have a researcher review the scientific claim and record unresolved issues.
6. Version the reviewed card. Keep older versions available when the recommendation changes.

## A future retrieval sequence

A user asks a question; the system filters cards by applicable scope and review state; search retrieves relevant passages; the model proposes a cited decision; structured tools enforce their input contract; results return as observations. A researcher handles unresolved scientific judgments.

Start with explicit card IDs or keyword search on a small library. Embeddings can help find paraphrases later, but exact gene IDs and accessions still need exact lookup. Retrieve the exception and prerequisite alongside the recommendation. A paragraph from a document must never gain authority to run arbitrary shell commands.

## Current status

This directory supplies learning cards, templates, a catalog and review records. It is not an installed LlamaIndex index, a LangChain agent or a production retrieval policy. Drafts are marked ineligible for future production retrieval; that field is documentation until runtime enforcement is implemented and tested. Benchmark hidden references and rewards belong outside agent-visible knowledge.

## Self-check

**Question:** If a guideline is placed in a vector database, has the agent learned it permanently?

**Suggested answer:** No. Retrieval supplies context for a particular request. Its availability, relevance and faithful use must still be tested.

## Implementation sources

- [collaboration/AGENT_DEVELOPMENT.md](https://github.com/Sculptor815/scrna-seq-workbench/blob/614917a5c0f678f0894acd3a3a1aa5f9542523de/collaboration/AGENT_DEVELOPMENT.md)
- [collaboration/knowledgebase/templates/EXPERIENCE.md](https://github.com/Sculptor815/scrna-seq-workbench/blob/614917a5c0f678f0894acd3a3a1aa5f9542523de/collaboration/knowledgebase/templates/EXPERIENCE.md)

[Learning path](../LEARNING_PATH.md) | [Review worksheet](../REVIEW_WORKSHEET.csv)
