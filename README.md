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
| **A · More tasks solved** | Same model and effort; paired verifier outcomes; uncertainty | Not established; final adjudication pending |
| **B · Comparable correctness, fewer tokens** | Correctness noninferiority first, then complete paired token accounting | Not established; final analysis pending |
| **B · Less money** | Observable, comparable monetary cost | Per-task subscription charges unavailable |

![Study coverage, provisional](public/studies/october-2026/coverage.svg)

The chart is a dated ledger snapshot, **not a leaderboard or final report**.
Execution finished on 27 October 2026 at 17:18 UTC: **352 scored cells and four
historical exclusions**, with no pending trials. This is execution completion,
not completion of the statistical analysis or evidence adjudication.
Recorded outcomes include unresolved verifier/infrastructure issues. We publish
negative and inconclusive findings as well as positive ones. No final investor
claim should be inferred from progress counts.

## One runner, explicit comparisons

| Harness | Integration | Evidence status |
|---|---|---|
| 80 Degrees | Frozen native engine adapter in crbn | Execution finished; analysis pending; medium only |
| Codex CLI | Pinned CLI adapter in crbn | Execution finished; analysis pending; version 0.163.0 |
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
