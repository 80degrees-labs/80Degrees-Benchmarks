# Final analysis and limitations

Analysis date: 28 October 2026. Terminal-Bench 2.0, medium reasoning,
80 Degrees native headless profile versus Codex CLI 0.163.0.
The evaluation comprises 352 scored cells and four historical exclusions.

## Claim decisions

**A - more tasks solved: not supported by this study.** Sol raw success tied at
62/87 per arm; Astra was 59/89 for 80 Degrees versus 65/89 for Codex. Exact paired
McNemar p-values are 1 and 0.2378845; Holm-adjusted values across the two models
are 1 and 0.4757690. Superiority criterion: not met.

**B - comparable correctness with fewer tokens: not established.** The predeclared
noninferiority margin is 5 percentage points. The conservative 95% one-sided lower
bounds for the paired success difference (80D minus Codex) are -11.84 points for
Sol and -19.85 for Astra, below the required -5 points. The combined correctness
and efficiency criterion is therefore unmet.

**B - modeled token cost: observed raw complete-pair totals favor 80 Degrees.**
At official Standard API rates checked 28 October, estimates are $11.23 vs $11.42
for Sol (1.6% lower) and $55.99 vs $63.68 for Astra (12.1% lower). See
[the complete cost calculation](COSTS.md). These are API-equivalent estimates;
subscription fees are excluded. Both-solved cost estimates are 3.9% higher for
Sol and 19.4% higher for Astra with 80 Degrees.

## Token results and uncertainty

Complete raw telemetry pairs: Sol 86, Astra 88. Native input-plus-output totals are
29,679,726 and 25,281,642; corresponding Codex totals are 38,966,944 and 34,886,113.
Ratios are 0.761664 and 0.724691, or 23.8% and 27.5% fewer recorded tokens.
Paired percentile bootstrap uses 50,000 samples and seed 10262026. Central 95%
ratio intervals are [0.563, 1.047] and [0.488, 1.035]. One-sided 95% upper bounds
are 0.995 and 0.984.

On resolved complete pairs, ratios are 0.662 (73 Sol pairs) and 0.923 (74 Astra
pairs). On both-solved pairs, ratios are 0.791 (56 Sol pairs) and 1.216 (53 Astra
pairs): Astra uses 21.6% more tokens on this selected subset. All subsets are
descriptive; selection by outcome limits causal interpretation.

Two native make-doom-for-mips timeout trials have no complete usage. Their matched
Codex trials are excluded from paired token totals, not correctness. Cached input
is a subset of total input; reasoning is a subset of output. Each is counted once.
Missing telemetry is reported as unavailable.

## Adjudication and sensitivity

The 356 slots comprise 248 verified passes, 58 verified failures, 31 verifier
Python-download timeouts, nine verifier network/package setup failures, two
interrupted package-manager setup failures, four mixed browser/assertion failures,
and four historical exclusions. There are 352 raw scored slots. The taxonomy
describes observed failure location rather than causal attribution. Agent actions
may affect package-manager state. Mixed browser errors remain failures in the raw
analysis and are treated as unknown in the expanded sensitivity analysis. Output
assertions, numerical mismatches, safety refusals and timeouts remain scored outcomes.

Unavailable-verifier outcomes are unknown, not credited passes. Restricting to
pairs without them leaves Sol 74 pairs (60 vs 61 successes) and Astra 75 pairs
(58 vs 60). Their conservative lower bounds are -13.58 and -16.09 points;
Holm-adjusted McNemar p-values are both 1. This exclusion is post-observation
sensitivity, not a replacement primary analysis.

Full 89-slot observed-difference bounds, allowing unavailable verifiers and
historical exclusions to take either outcome: Sol [-14.61, +14.61] points; Astra
[-15.73, +6.74] points. Including mixed browser failures widens these to
[-15.73, +15.73] and [-16.85, +7.87]. These are identification bounds, not confidence
intervals. Neither the raw nor sensitivity evidence supports the proposed claims.

## Reservations and consumption

370 ledger reservations: 352 scored, 10 historical, seven explicit provider
capacity failures and one local failure before Harbor/model launch. Historical
reservations cover four excluded cells and count toward the cap. These outcomes
are not best-of-three pass rates. Four reused synthetic preflights are outside
this ledger. Consumption totals therefore cover ledger reservations only.

| Model / arm | Reservations | Complete-usage attempts | Observed token subtotal |
|---|---:|---:|---:|
| Sol / 80 Degrees | 97 | 89 | 30,152,859 |
| Sol / Codex | 94 | 90 | 43,298,117 |
| Astra / 80 Degrees | 89 | 88 | 25,281,642 |
| Astra / Codex | 90 | 89 | 37,253,530 |

These are observed subtotals with unequal missingness, not complete consumption
comparisons. The 14 reservations without complete usage include a known zero-call
local failure; provider-error zero placeholders are treated as unmeasured.

## Reproduce and review

From the repository root, install `tooling/analysis-requirements.txt` in a private
environment, then run:

```sh
python tooling/final_analysis.py
python tooling/price_usage.py
python tooling/build_reports.py
python -m unittest discover -s tests -v
python tooling/audit_public.py
```

The public `task-results.json` and `attempts.json` reproduce the statistics without
raw logs. `--export-private` is only for the study owner's private ledger. The
export is an explicit allowlist of scalar fields; no transcripts or credentials
are copied. Task and attempt rows carry result/verifier content hashes, while
`provenance.json` identifies versions and source artifacts. Independent validation
requires access to authorized redacted source evidence. Hashes support artifact
integrity checks. PDF reports are generated locally and visually reviewed; charts
are derived from the published numeric data.

The original protocol followed pilot observations. Hardware emulation, shared
subscription, sequential models and incomplete verifiers limit generalization.
Same model/effort was verified by the frozen controller in every scored cell;
paired task checksums match. Later portable adapters were not used in this study.

## Scope and follow-up evaluation

The 42 unavailable-verifier trials have no retained solution artifacts or original
containers suitable for verifier-only replay. Their outcomes remain unresolved.
Historical attempts remain included in the three-attempt cap.

Follow-up evaluation should specify a new protocol, pinned verifier dependencies,
prospective sample-size planning and an independent holdout following harness
refinement. The present findings apply to the measured profiles and medium-reasoning
Terminal-Bench 2.0 run; SWE-bench, high reasoning and other competitor CLIs are
outside the evaluated scope. The analysis was conducted by the study owner and has
not undergone independent replication.
