# Releases and versioning

Use Semantic Versioning.

- **MAJOR:** incompatible API, data, deployment, or user-workflow changes requiring migration.
- **MINOR:** backward-compatible user-visible features or substantial new capabilities.
- **PATCH:** backward-compatible fixes, hardening, and documentation corrections when a release is justified.

No GitHub releases are currently published, so the README intentionally has no release badge.

## Release trigger

A merge alone does not require a release. Create a release when a coherent, tested set of changes is useful to users/operators and has:
- green required CI/security checks,
- updated README/SPRINTS/BACKLOG/documentation,
- migration/rollback guidance where applicable,
- verified badge/license state,
- release notes describing user-visible impact.

The first stable `v1.0.0` should require an explicitly accepted SMB-ready MVP contract, documented deployment/upgrade path, stable data/visibility behavior, and validated CI/security checks. Until then, use `v0.x.y` if tagged releases become useful.
