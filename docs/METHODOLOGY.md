# Claim contract

The [28 October final analysis](../public/studies/october-2026/RESULTS.md)
reports observed outcomes, statistical decisions and sensitivity analyses under
this protocol.

The October study compares 89 Terminal-Bench 2.0 tasks, two models and two harnesses
(356 slots), with medium reasoning only. Models are gpt-6.1-sol and gpt-6-astra.
Four slots use historical adapters and are excluded from the frozen primary
cohort. Earlier outcomes were observed before the full protocol; this is not a
pristine preregistration. SWE-bench Verified is outside this study.

Use the same tasks, verifier, limits and model per paired comparison. Record
model IDs observed at runtime, provider, effort, service tier, tools, prompts,
source and engine commits, dirty-tree changes, exact CLI/Harbor/dataset versions,
container digests, architecture and auth type. Never publish auth values.

Claim A requires a positive effect with conservative uncertainty and exact paired
McNemar testing, Holm-adjusted across the two models. Include worst-case missing
outcome sensitivity. Do not select only favorable tasks or models.

Claim B first requires correctness noninferiority at a predeclared 5 percentage
point margin: lower one-sided paired difference bound > -0.05. For October,
subtract the exact upper loss-probability bound from the lower win-probability
bound, each using alpha .025 (union bound coverage at least 95%). Then require
the paired bootstrap upper 95% aggregate token-ratio bound < 1. Report sample
size and missing usage. Cached input is part of input; reasoning is part of
output. Never add either twice or impute missing telemetry as zero. Report both
primary-attempt usage and all-attempt consumption, with a deterministic bootstrap
seed and sensitivity analyses. Both-solved subsets are descriptive only.

Keep all failures. Classify from evidence: provider capacity, quota/auth,
container/infrastructure, verifier failure, agent failure or unresolved. A failed
verifier download is not automatically an incorrect solution. Safety refusals
remain agent outcomes. Never retry a scored failure to improve its score.
October's capacity retry amendment allows a 300-second delay and at most three
total launches, counting historical attempts. Unknown failures stop for review.

Subscription billing provides no reliable per-task actual dollars. API-price
equivalents, if published, must be separately labeled estimates with dated rates.
Incomplete data cannot establish either claim. An identity-unverified portable
profile cannot establish a same-model claim even if the verifier passes.

Publish a protocol and amendment history, paired task table, missingness table,
exact versions, failure classifications, uncertainty, limitations and claim
verdicts. Improvements learned from these tasks require a new held-out evaluation.
