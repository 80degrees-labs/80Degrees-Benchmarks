# Standard API-equivalent costs

Calculated 28 October 2026 using official model prices. This is a retrospective
rate-normalized estimate of recorded text-token usage, **not actual subscription
charges**, a quote for a future run, or the cost of the whole project.
This post-analysis cost extension retains the original task scores, retry rules
and noninferiority margin.

## Rates per million tokens, USD

| Model | Uncached input | Cache read | 30m cache write | Output |
|---|---:|---:|---:|---:|
| gpt-6.1-sol | 2.00 | 0.10 | 2.50 | 10.00 |
| gpt-6-astra | 10.00 | 1.00 | 12.50 | 50.00 |

Sources: [pricing](https://developers.openai.com/api/docs/pricing),
[Sol model](https://developers.openai.com/api/docs/models/gpt-6.1-sol),
[Astra model](https://developers.openai.com/api/docs/models/gpt-6-astra).
Standard tier assumed equally for both arms. Above 272K input tokens per request,
the applicable input/cache rates double and output rate increases by 50%.
No such request was found in the audited eligible traces. No regional uplift,
priority premium, tax, hosted-tool fee or subscription allocation is included.

## Formula and audit

`USD = ((input - cache_read - cache_write) * input_rate + cache_read * read_rate + cache_write * write_rate + output * output_rate) / 1,000,000`

Reasoning is part of output; cached tokens are part of input. The records show
zero cache writes. The calculation applies category-specific token rates.
The 350 scored cells with complete aggregate usage were checked against native
message usage or Codex session token events; repeated cumulative Codex updates
are deduplicated. Two native traces have small residuals between event sums and
aggregate totals, each below 272K input, so they cannot change the context tier.
All costs use aggregate totals, including the event-to-aggregate residuals.
`pricing-audit.json` records numeric diagnostics and source hashes without traces.

Paired cost comparisons require complete data on both arms: 86 Sol and 88 Astra
pairs. Timeout usage, historical reservations and failed-attempt consumption are
excluded here. These estimates do not imply identical caching in a real API replay.

| Subset | Sol 80D / Codex | Astra 80D / Codex |
|---|---:|---:|
| Raw complete pairs | $11.23 / $11.42 | $55.99 / $63.68 |
| Observed reduction | 1.6% | 12.1% |
| Resolved complete pairs | $8.34 / $8.82 | $45.93 / $44.91 |
| Both-solved pairs | $5.67 / $5.45 | $33.50 / $28.06 |

The observed raw totals favor 80 Degrees. Both-solved totals favor Codex by 3.9%
on Sol and 19.4% on Astra (80D relative excess). Raw paired-bootstrap central 95%
cost-ratio intervals are [0.834, 1.159] and [0.689, 1.105]; both include 1. These
descriptive cost results do not satisfy the failed correctness noninferiority gate.
Subset selection is not causal evidence of efficiency at equivalent correctness.

Reproduce using `python tooling/price_usage.py` with the analysis dependencies.
`--export-private` rebuilds the numeric trace audit only on the owner's machine.
The original statistical analysis and raw task scores are unchanged.
