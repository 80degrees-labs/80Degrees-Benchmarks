# Contributing evidence

1. Open an issue describing the benchmark, harness, exact model and question.
2. Freeze the protocol before observing outcomes: task selection, seed, effort,
   limits, retry rules, exclusion rules, statistics and cost basis.
3. Validate the adapter with a synthetic task. Prove the effective runtime model,
   effort and CLI version; check errors embedded in successful process output.
4. Run in disposable containers. Preserve every launch, error and verifier result.
   Resume the original ledger; never reset attempt counts in a new directory.
5. Submit a pull request under `public/studies/<unique-study-id>/` with a report,
   sanitized task-level results, coverage, missing usage, provenance, methodology,
   hashes of retained raw artifacts and a redaction manifest. Provide a way for
   reviewers to request appropriately redacted supporting evidence.
6. Run `python3 tooling/audit_public.py` and offline tests, then manually inspect
   `git diff --cached`. Do not upload raw logs, credentials, prompts copied from
   restricted datasets, local usernames/paths, session/account IDs or private code.

Required task rows: study ID, task ID, harness/version, model/effort requested and
observed, identity verification, attempt index, outcome classification, reward,
input/output/cache tokens (nullable), cost basis (nullable), verifier provenance
and artifact hashes. Distinguish historical, excluded and unresolved rows.

Results must include losses and inconclusive findings. Cross-model comparisons
need explicit labels; they cannot substantiate the same-model claim. New adapters
must fail on identity mismatch, preserve raw evidence privately and never invent
usage. Offline tests must cover quoting, errors, missing telemetry and resumption.
Adding a config template alone does not make an integration benchmark-validated.

Keep implementation changes in [crbn](https://github.com/aniasusual/crbn), and
link the exact source commit from your result submission. Submit learning notes
as observed evidence, hypotheses and proposed experiments in separate sections.
Do not tune an active frozen study in response to results.
