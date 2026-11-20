# Agent operating instructions

This repository follows the Mad Mallard Development Standards and the shared guidance in `drakeg/madmallard-repository-standards`. Project-specific requirements in this repository take precedence when they are stricter.

## Operating model

1. Work in the cycle **Build → Deploy → Test → Fix → Redeploy → Continue**.
2. Do not stop because a sprint ends, a PR opens, CI passes, or a deployment succeeds. Continue to the next ready task while respecting review/merge boundaries.
3. Use feature branches and reviewable pull requests. Do not merge owner-review PRs unless explicitly authorized.
4. Treat failed builds, tests, CI, deployments, accessibility checks, and application regressions as P0/P1 work.
5. Keep `SPRINTS.md`, `BACKLOG.md`, `RELEASES.md`, README, and relevant docs synchronized with behavior.
6. Preserve existing data. Do not enable live payments, paid infrastructure, production failover, or destructive migrations without explicit authorization.
7. Keep this repository independent from other applications. Shared standards are policy/templates only, not shared application services.
8. Prefer Docker Compose for local testing. Local test deployments should support explicit trusted-LAN access through `.env`.
9. Keep dependencies on supported secure versions; prefer supported LTS/stable releases where applicable.
10. Never claim a test, deployment, release, security result, customer, revenue, or market validation that was not actually verified.

## GitHub and README badges

- Keep the bounded Mad Mallard badge block immediately below the README H1.
- Badge claims must be backed by repository configuration, manifests, workflows, releases, licenses, or infrastructure.
- Use dynamic GitHub Actions, issue, PR, release, and license badges when applicable.
- Do not hardcode passing CI/security status.
- Run `python3 scripts/badges.py --mode check` and `python3 scripts/audit.py --check` when standards-related files change.
- Update badge detection when supported technologies, workflows, release state, or licensing change.

## ytclone-specific guardrails

- Centralize visibility through `Video.objects.visible_to(user)` and existing permission services.
- Keep business logic in services where practical; views/templates should remain thin.
- Add regression tests for user-visible behavior and visibility/authorization boundaries.
- Live Stripe activation, real payouts/bank management, production AWS resources, and paid services require explicit owner approval.
- Local Docker/LAN behavior is a supported development workflow; production exposure is not implied.
