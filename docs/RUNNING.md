# Run a benchmark

## Prerequisites

Use Python 3.12+, Git, Docker, Harbor, the latest
[80 Degrees source](https://github.com/aniasusual/crbn) with its Harbor adapter,
and your chosen competitor CLI version. Record the installed versions and source
commits when preparing the study, then keep them fixed throughout that run.
Published study versions are recorded in each study's provenance file.

Install Harbor in a private virtual environment.
Export `PYTHONPATH` to the absolute `crbn/benchmarks/harbor` directory. Record
`harbor --version`, source revisions and container image digests before execution.
Use Linux x86_64 task images; Apple Silicon emulation must be disclosed.

Build the native `runner.ts` with the Bun version required by your checkout, using `--target=bun` and
`--external omp-legacy-pi-modules`. Its staged bundle needs `runner.js`, its
generated assets, `bun-linux-x64/bun`, the checkout's matching Linux x64 baseline pi-natives
addon in `native/`, and `ca-certificates.crt`. Follow the source adapter's expected
layout. Pin the engine checkout independently of the parent repository gitlink.
Runtime dependencies must be provisioned locally; they are not distributed in this repository.

For Codex, set `BENCH_CODEX_DIST` to the unpacked Linux distribution of your selected CLI version,
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

Choose a model/provider and reasoning setting supported by both configured
harnesses. Validate the native provider profile and competitor profile together
before a same-model comparison. The supplied native profile targets Codex-backed
models; Claude, Gemini and DeepSeek comparisons require a matching native provider
integration in the selected 80 Degrees checkout.

## Prepare, validate, run

```bash
python3 tooling/study.py prepare private/spec.json --output private/new-study
python3 tooling/study.py run --output private/new-study
```

Preparation writes immutable config hashes and a durable launch ledger. Before
the full dataset, use a separate synthetic task study to verify installation,
auth, tool execution, verifier output, exact runtime model and telemetry. This
validation uses model allowance. Confirm credentials and budget before launch.

The new runner runs one cell at a time, at most three total attempts. On a
failure it stops. Preserve and classify the error, check that no process remains,
then use `run --retry-failed` only for adjudicated infrastructure failures.
Successful scored zeroes are completed cells, never retry targets. An orphaned
running reservation requires reconciliation with raw evidence; the runner refuses
to guess. No automatic quota retry, fallback or model change is performed.
Keep the same output directory across resumes. Prior studies/paid preflights must
be included in your protocol and cap accounting; the new runner cannot infer them.

## Publish

Use the contribution schema for final reviewed results. Keep raw data private,
produce a redaction manifest and hashes, and run `python3 tooling/audit_public.py`.
Review `git status --short` and every staged diff. No tool here commits or pushes.
