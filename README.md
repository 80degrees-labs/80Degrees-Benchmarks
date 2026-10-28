<div align="center">

# 80 Degrees · Benchmarks

**Evidence you can inspect. Comparisons you can reproduce.**

[Harness source](https://github.com/aniasusual/crbn) · [Methodology](docs/METHODOLOGY.md) · [Run a comparison](docs/RUNNING.md) · [Contribute evidence](CONTRIBUTING.md)

</div>

This repository holds evaluation protocols, sanitized results, reports and lessons
from comparing **80 Degrees** with other coding agents through
[Harbor](https://github.com/harbor-framework/harbor). The application and adapter
implementation belong in **crbn**; this repository owns the evidence and study tools.

## Evidence, before claims

| Question | Required evidence | Current conclusion |
|---|---|---|
| **A · More tasks solved** | Same model and effort; paired verifier outcomes; uncertainty | **Not supported by this study.** Raw Sol tied; raw Astra favored Codex. Neither superiority test passed. |
| **B · Comparable correctness, fewer tokens** | Correctness noninferiority first, then complete paired token accounting | **Not established.** Both models failed the predeclared correctness evidence gate, despite lower raw complete-pair token totals. |
| **B · Less money** | Observable, comparable monetary cost | **Not measurable from these data.** Subscription access provides no actual per-task dollar charges. |

![Study coverage, provisional](public/studies/october-2026/coverage.svg)

The chart is a dated ledger snapshot, **not a leaderboard or final report**.
Execution finished on 27 October 2026 at 17:18 UTC: **352 scored cells and four
historical exclusions**, with no pending trials. The **available-evidence analysis
is complete as of 28 October**. Unresolved outcomes remain unknown; completion of
analysis does not make the evidence complete. No additional paid runs were made.

### Reports and evidence

- [Investor assessment (PDF)](public/studies/october-2026/reports/80degrees-investor-benchmark-report.pdf)
- [Harness refinement report (PDF)](public/studies/october-2026/reports/80degrees-harness-refinement-report.pdf)
- [Final analysis and limitations](public/studies/october-2026/RESULTS.md)
- [Task-level CSV](public/studies/october-2026/task-results.csv), [analysis JSON](public/studies/october-2026/analysis.json), [attempt accounting](public/studies/october-2026/attempts.json), [provenance and redaction](public/studies/october-2026/provenance.json)

| Medium reasoning | Raw paired success: 80 Degrees / Codex | Raw token reduction* | Correctness lower bound** |
|---|---:|---:|---:|
| 6.1 Sol | 62/87 / 62/87 (71.3% / 71.3%) | 23.8% (86 complete pairs) | -11.84 percentage points |
| 6 Astra | 59/89 / 65/89 (66.3% / 73.0%) | 27.5% (88 complete pairs) | -19.85 percentage points |

\* Input plus output, cached input counted once. Complete scored pairs only;
failed-attempt consumption and missing telemetry are not included in these ratios.
\** Conservative 95% one-sided bound for 80 Degrees minus Codex. The predeclared
noninferiority requirement is a lower bound above **-5 points**. Neither passes.
Equal observed success does not prove equivalence; failure of noninferiority does
not by itself prove inferiority. Exact McNemar Holm-adjusted p-values are 1.0000
and 0.4758, respectively.

![Raw paired correctness](public/studies/october-2026/charts/correctness.svg)
![Paired outcome pie charts](public/studies/october-2026/charts/paired-outcomes.svg)
![Token ratios by evidence subset](public/studies/october-2026/charts/token-ratios.svg)

On tasks **both harnesses solve**, Sol uses 20.9% fewer tokens, but Astra uses
**21.6% more**. These selected subsets are descriptive. They are not evidence of
comparable overall correctness. Two-sided 95% bootstrap intervals for the raw
token ratios include 1 for both models; detailed bounds are in the reports.

![Evidence-quality pie chart](public/studies/october-2026/charts/evidence-quality.svg)

The audit identifies 42 scored zeroes with an unavailable verifier, four mixed
browser/assertion failures and four historical exclusions. Raw scores are retained.
Resolved-pair and missing-outcome sensitivity analyses also do not establish the
claims. These are first-party findings, not an independent audit or certification.

## One runner, explicit comparisons

| Harness | Integration | Evidence status |
|---|---|---|
| 80 Degrees | Frozen native engine adapter in crbn | Available-evidence analysis complete; medium only |
| Codex CLI | Pinned CLI adapter in crbn | Available-evidence analysis complete; version 0.163.0 |
| Claude Code | Version-checked portable CLI profile | Experimental; no scored validation here |
| Cursor Agent | Version-checked portable CLI profile | Experimental; effort mapping must be verified |
| Google Antigravity CLI | Version-checked portable CLI profile | Experimental; no scored validation here |
| Your harness | Harbor `import_path` or portable CLI profile | Contributor must validate identity and usage |

Different products need their own supported credentials. A Codex subscription
does not authenticate competing services. A provider such as DeepSeek is not a
harness: record both the model/provider and the agent software. Matching a label
such as “medium” across providers does not prove equal inference settings.

## Get started

See [the complete setup](docs/RUNNING.md). Preparing a study is free of model calls:

```bash
python3 tooling/study.py prepare examples/study.json --output private/my-study
# After replacing placeholders and reviewing the generated manifest/configs:
python3 tooling/study.py run --output private/my-study
```

The runner reserves each attempt durably before launch, runs serially, never
reruns completed jobs and stops on errors. Retries require explicit resumption
and remain capped at three total launches per cell. Keep the same study directory.
The existing October controller and its historical ledger remain separate and
private; this new runner does not migrate or restart them.

## Repository map

```text
docs/          Methodology, setup, publication rules
examples/      Editable study and competitor profiles (no credentials)
tooling/       Durable runner, safe snapshot export, publication audit
tests/         Offline validation; no model usage
public/        Reviewed, sanitized evidence and reproducible charts
```

Raw transcripts, credentials, local runtime bundles, private ledgers and task
checkouts are excluded by default. `.gitignore` is not a sanitizer: use the
publication audit and review every staged file before sharing. The live study's
raw evidence is retained locally for audit, not automatically published.

## Participate

Follow [CONTRIBUTING.md](CONTRIBUTING.md) to submit a reproducible study, adapter
validation or a documented limitation. Community results remain attributed to
their authors until reviewed; submitting a result does not endorse either claim.

No license is granted here for third-party datasets, models, CLIs or transcripts.
Check their terms before redistributing artifacts. This repository is an
independent evaluation project and is not endorsed by the compared vendors.
