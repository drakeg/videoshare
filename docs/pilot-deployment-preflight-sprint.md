# SMB Pilot Deployment Preflight Sprint

## Goal

Add a repeatable preflight command that tells an operator whether a VideoShare deployment is configured safely and appropriately before an SMB demo or pilot.

## Scope

- Add a reusable preflight service with PASS/WARN/FAIL results.
- Add `python manage.py pilot_check`.
- Support `--profile public` and `--profile private`.
- Support `--deployment` for stricter production-style HTTPS/debug checks.
- Fail on unsafe wildcard hosts and the committed example secret.
- For private pilots, require private-portal mode and disabled public registration.
- Warn when the default VideoShare brand is still in use.
- Warn when debug mode is enabled unless deployment checks are explicitly requested; deployment mode treats debug/insecure cookies/redirects as failures.
- Keep the command read-only: no settings, data, users, infrastructure, or secrets are modified.
- Document the preflight workflow in the README and deployment guidance.

## Commercial rationale

Pilot setup errors create support cost and can undermine a customer demo. A single deterministic command gives operators a fast go/no-go check for branding, access policy, host security, and deployment hardening without requiring paid infrastructure or manual code review.

## Acceptance criteria

1. The default public profile can run against normal local development settings and clearly reports warnings rather than mutating configuration.
2. Private profile fails when private-portal mode is disabled or public registration remains enabled.
3. Private profile passes those access-policy checks when configured correctly.
4. Wildcard allowed hosts and the example secret are always failures.
5. Deployment mode fails on debug mode, disabled HTTPS redirect, or insecure session/CSRF cookies.
6. Default site branding is a warning, not a failure.
7. The command exits non-zero when any FAIL result exists.
8. Output includes actionable environment-variable guidance for every warning/failure.
9. Focused tests cover public/private/deployment profiles and exit behavior.
10. No migration, dependency, paid service, live-payment, or AWS resource change is introduced.

## Verification

    python manage.py check
    python manage.py makemigrations --check --dry-run
    python manage.py test video.test_pilot_preflight
    python manage.py test --parallel 4
    python manage.py pilot_check --profile public
    docker compose config --quiet

## Out of scope

- Provisioning infrastructure
- Creating users
- SSO/OIDC/SAML
- DNS/TLS automation
- Live Stripe activation
- Automatic secret generation or settings mutation

## Delivered

- Added reusable PASS/WARN/FAIL pilot-preflight evaluation.
- Added `manage.py pilot_check` with public/private profiles and optional deployment hardening.
- Added failures for wildcard hosts and the committed example secret.
- Added private-pilot policy checks for login gating and closed registration.
- Added deployment checks for debug mode, HTTPS redirect, and secure session/CSRF cookies.
- Added branding and payment-provider guidance without enabling live payments.
- Added operator documentation and README workflow.
- Added 11 focused regression tests.

## Verification results

- Focused Docker tests passed 11/11 in 0.039s.
- Real local public-profile preflight reported 4 PASS, 2 WARN, 0 FAIL.
- `python3 -m compileall -q video yt` passed locally.
- `git diff --check` passed locally.
- `docker compose config --quiet` passed locally.
- GitHub Actions Django checks run #648 passed configuration and migration-drift checks and all 945 tests with one expected skip.
- Repository standards workflow run #10 passed.
- A full serial local Docker suite was also launched and was still progressing normally when this closeout was prepared; no full-local pass is claimed here unless a later closeout update records completion.
