# Run a separate comparison

## Prerequisites

Use Python 3.12+, Git, Docker and a pinned Harbor checkout. For the October
study, Harbor commit is `209a48a7424218828465c3c716b042f2b381dbed` (0.24.0),
Terminal-Bench 2.0 is `69671fbaac6d67a7ef0dfec016cc38a64ef7a77c`, and
80 Degrees' measured adapter is `770667538eb64aae2169b4006aa41ee781ae994c`.
New integration code on `feat/benchmark-harbor` is not the measured October code.
The native engine checkout was `028c1d7c7eb753421012bf96472a4ea040667f19`.

Clone [crbn](https://github.com/aniasusual/crbn) and select a specific adapter
commit. Install Harbor from a pinned commit in a private virtual environment.
Export `PYTHONPATH` to the absolute `crbn/benchmarks/harbor` directory. Record
`harbor --version`, source revisions and container image digests before execution.
Use Linux x86_64 task images; Apple Silicon emulation must be disclosed.

Build the native `runner.ts` using Bun 1.4.3 with `--target=bun` and
`--external omp-legacy-pi-modules`. Its staged bundle needs `runner.js`, its
generated assets, `bun-linux-x64/bun`, the Linux x64 baseline pi-natives 18.12.3
addon in `native/`, and `ca-certificates.crt`. Follow the source adapter's expected
layout. Pin the engine checkout independently of the parent repository gitlink.
Runtime dependencies must be provisioned locally; they are not distributed in this repository.

For Codex, set `BENCH_CODEX_DIST` to the pinned unpacked Linux distribution,
`BENCH_CA_BUNDLE` to a public CA certificate bundle, and `CODEX_AUTH_JSON_PATH`
to your own subscription credential. Do not copy these files into public evidence.

## Configure

Copy `examples/study.json` to a private location and replace every `REPLACE` field.
Supply the full predeclared task list and exactly versioned Harbor agent configs.
Replace an arm with `examples/claude-code.json`, `cursor.json` or `antigravity.json`
to use the experimental portable adapter. Any Harbor custom `import_path` is
supported, so a DeepSeek-backed harness can provide its own adapter and model ID.

Portable profiles require a Linux bundle containing the CLI at `bin/<name>` and
all required dependencies, or an explicitly recorded preinstalled image. They do
not install floating latest versions. Provision supported authentication yourself;
only listed `env_names` are passed, and their values are never written to the
manifest. Antigravity has no assumed credential variable in the example: configure
its supported container auth before use. Cursor's example does not expose an
effort flag; use a documented model/effort mapping and verify it in raw output.
If no matching effort exists, label the comparison unmatched.

The 80 Degrees frozen adapter supports the two Codex models at medium only. A
comparison with a Claude/Gemini/DeepSeek model needs a separately implemented,
validated native provider profile in crbn before it can test same-model claims.
The portable competitor configs do not add those providers to 80 Degrees.

## Prepare, validate, run

```bash
python3 tooling/study.py prepare private/spec.json --output private/new-study
python3 tooling/study.py run --output private/new-study
```

Preparation writes immutable config hashes and a durable launch ledger. Before
the full dataset, use a separate synthetic task study to verify installation,
auth, tool execution, verifier output, exact runtime model and telemetry. This
validation uses model allowance; do not launch until credentials and budget are
ready. No integration is certified merely because configuration generation passes.

The new runner runs one cell at a time, at most three total attempts. On a
failure it stops. Preserve and classify the error, check that no process remains,
then use `run --retry-failed` only for adjudicated infrastructure failures.
Successful scored zeroes are completed cells, never retry targets. An orphaned
running reservation requires reconciliation with raw evidence; the runner refuses
to guess. No automatic quota retry, fallback or model change is performed.
Keep the same output directory across resumes. Prior studies/paid preflights must
be included in your protocol and cap accounting; the new runner cannot infer them.

## Publish

The October progress-only export is `python3 tooling/export_progress.py`; it reads
the local ledger and copies only allowlisted counts and version metadata. It does
not certify a process is running or generate final claim verdicts. Its SVG chart
is deterministic geometry derived from counts, with a timestamp, not AI artwork.

Use the contribution schema for final reviewed results. Keep raw data private,
produce a redaction manifest and hashes, and run `python3 tooling/audit_public.py`.
Review `git status --short` and every staged diff. No tool here commits or pushes.
