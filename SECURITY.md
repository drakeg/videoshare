# Security policy

Do not submit credentials, sensitive customer data, private media, or working exploits in public issues. Use GitHub private vulnerability reporting if enabled, or contact the repository owner privately before sharing sensitive details.

## Supported code

Until a stable release line exists, security fixes target the current default branch.

## Development security

- Workflows should use least privilege; read-only `contents` is the default.
- Production secrets must never be exposed to pull requests, logs, test fixtures, or local documentation.
- Review dependency and GitHub Action changes before merge.
- Keep video visibility and channel moderation boundaries covered by regression tests.
- Live payment credentials, production AWS provisioning, and public deployment require explicit authorization.
- Dependency auditing is automated in `.github/workflows/security.yml`; a green workflow means the configured audit completed, not that the application is vulnerability-free.
