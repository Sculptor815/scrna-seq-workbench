# v0.3.0 - biological questions and focused analysis

The new scrna-research entry point guides study selection and routes a biological
question to the relevant analysis stages. It supports delegated routine settings,
documents dataset suitability and evidence, and distinguishes exploratory results
from stronger inference. Study discovery uses the host's existing search tools.

The new research command exports donor expression, equal-donor condition summaries
and an HTML report from declared counts and documented labels. It preserves input
files, identifies missing genes and retains low-support groups in the detailed
table. It does not assign inferential significance or validate labels.

Developer evaluation is separate on the benchmark branch under benchmarks/research. Its calculator consumes
documented final reviews and reports weighted ratings and eligibility. It is excluded
from plugin archives and never invoked by user analysis Skills. No new scientific
benchmark scores are claimed. Historical evidence and HPA review status are unchanged.

See docs/RESEARCH_WORKFLOW.md for usage and validation.json for release checks.
