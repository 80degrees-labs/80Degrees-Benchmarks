# Publication boundary

Never submit secrets in an issue or pull request. If a secret is accidentally
published, revoke it immediately and contact the repository owner privately;
deleting a file does not remove it from Git history.

Only the explicit public directories are eligible for tracking. Raw trial output
may contain credentials, customer data, task text or machine identifiers.
The export tool constructs a small allowlisted aggregate rather than copying logs.
The publication audit is an additional check, not a guarantee of safe content.
Do not use `git add -f` to bypass these protections. Review all staged changes.

No benchmark or installation runs in CI by default. Competitor CLI profiles can
execute arbitrary task commands and belong only in disposable benchmark containers,
with dedicated minimally scoped credentials and no host home-directory mounts.
