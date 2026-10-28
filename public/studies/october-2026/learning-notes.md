# Harness development observations

Task-level observations supporting harness development. The final analysis is in
[RESULTS.md](RESULTS.md). PDF reports are retained locally, not published here.

These are observations from private raw evidence, not adjudicated causal findings
or final claim results. No active-study tuning was performed in response.

| Task | Observed issue in 80 Degrees | Follow-up hypothesis |
|---|---|---|
| rstan-to-pystan | Final response preceded verified output CSVs | Check completion handling for background work |
| compile-compcert | Build still pending; expected compiler absent | Check lifecycle and budget handling before final response |
| protein-assembly | Asked for clarification; required output absent | Investigate interactive assumptions in a headless task |
| mteb-leaderboard | Selected model differed from expected answer | Review source/date ambiguity before attributing harness failure |
| overfull-hbox | Verifier dependency download timed out | Adjudicate infrastructure separately from solution correctness |
| make-doom-for-mips | Native token telemetry missing | Investigate telemetry completeness; never impute zero |

Correctness priorities include completion handling and verifier reliability.
Efficiency analysis requires complete paired telemetry and the predeclared
correctness noninferiority criterion. Both-solved subsets are outcome-selected
and descriptive. These observations constitute development data; subsequent
validation requires independent held-out tasks.

Evidence access: raw artifacts are retained privately because logs can expose
credentials, local identifiers and task content. Public task rows, redaction
provenance and supporting evidence hashes accompany the final analysis.
