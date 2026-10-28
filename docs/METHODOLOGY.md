# Benchmark methodology

The [28 October final analysis](../public/studies/october-2026/RESULTS.md)
reports observed outcomes, statistical decisions and sensitivity analyses under
this protocol.

## Study design

Each study defines its task set, harnesses, models, reasoning effort, resource
limits and decision criteria before execution. New studies use the selected
80 Degrees checkout and competitor CLI versions, recorded and fixed for the run.
The October study contains 89 Terminal-Bench 2.0 tasks, two models
(gpt-6.1-sol and gpt-6-astra), two harnesses and medium reasoning: 356 task cells.
Study-specific exclusions and limitations are recorded in the final analysis.

Use the same tasks, verifier, limits and model per paired comparison. Record
model IDs observed at runtime, provider, effort, service tier, tools, prompts,
source and engine commits, dirty-tree changes, exact CLI/Harbor/dataset versions,
container digests, architecture and auth type. Never publish auth values.

## Claim A: task success

Claim A requires a positive effect with conservative uncertainty and exact paired
McNemar testing, Holm-adjusted across the two models. Include worst-case missing
outcome sensitivity. Analysis covers the full declared task and model set.

## Claim B: correctness and token efficiency

Claim B first requires correctness noninferiority at a predeclared 5 percentage
point margin: lower one-sided paired difference bound > -0.05. For October,
subtract the exact upper loss-probability bound from the lower win-probability
bound, each using alpha .025 (union bound coverage at least 95%). Then require
the paired bootstrap upper 95% aggregate token-ratio bound < 1. Report sample
size and missing usage. Cached input is part of input; reasoning is part of
output. Count each once and report missing telemetry as unavailable. Report both
primary-attempt usage and all-attempt consumption, with a deterministic bootstrap
seed and sensitivity analyses. Both-solved subsets are descriptive only.

## Failure handling

Retain every attempt and classify its evidence: provider capacity, quota/auth,
container/infrastructure, verifier failure, agent failure or unresolved.
Verifier availability is recorded separately from solution correctness. Safety
refusals remain agent outcomes. Scored failures are completed observations.
October's capacity retry amendment allows a 300-second delay and at most three
total launches, counting historical attempts. Unknown failures stop for review.

## Cost accounting

Standard API-equivalent estimates apply dated input, cached-input and output
rates to recorded usage. Publish rates, sources, eligible pairs, exclusions and
uncertainty alongside estimated totals. Actual expenditure requires comparable
billing records. Subscription fees are separate from API-equivalent estimates.

## Publication

Publish a protocol and amendment history, paired task table, missingness table,
exact versions, failure classifications, uncertainty, limitations and claim
verdicts. Same-model comparisons require verified runtime model and effort.
Harness improvements are evaluated on an independent held-out task set.
