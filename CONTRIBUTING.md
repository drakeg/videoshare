# Contributing

Contributions, including AI-authored changes, should be small, reviewable, tested, and tied to the current sprint or prioritized backlog.

## Workflow

1. Start from current `main` and use a scoped feature/fix/docs branch.
2. Document the sprint goal, business/user rationale, acceptance criteria, and exclusions before feature implementation.
3. Prefer Conventional Commits such as `feat:`, `fix:`, `docs:`, `test:`, and `chore:`.
4. Add or update regression tests and documentation with behavior changes.
5. Run the relevant focused tests, then the full Django checks. For Docker-affecting changes, run the Compose checks and real local workflow.
6. Open a PR summarizing impact, test evidence, risk/rollback, migration needs, security considerations, and release impact.
7. Resolve CI failures before merge. Human review is required for owner-review PRs.

## Standard checks

```bash
python3 scripts/audit.py --check
python3 scripts/badges.py --mode check
python3 -m unittest discover -s tests -v
python3 -m compileall -q video monetization yt
docker compose config --quiet
docker compose run --rm --entrypoint python test manage.py check
docker compose run --rm --entrypoint python test manage.py makemigrations --check --dry-run
docker compose run --rm --entrypoint python test manage.py test
```

## Definition of ready

A task has a clear customer/user benefit, acceptance criteria, boundaries, dependencies, and scope small enough for a sprint. Commercial features should identify the target SMB problem and how the task advances a demo, pilot, or paying-customer path.

## Definition of done

Acceptance criteria are met; focused and full tests pass; security/standards checks pass; documentation and badges are current; no secrets are exposed; release impact is recorded; and the PR is reviewable.
