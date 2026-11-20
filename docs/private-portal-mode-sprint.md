# Private Portal Mode Sprint

## Goal

Add an opt-in login-required deployment mode for SMB training, coaching, client, and internal-video pilots without changing the default public VideoShare behavior.

## Scope

- Add `DJANGO_PRIVATE_PORTAL=false` as the default.
- When enabled, require authentication for application pages through one middleware gate instead of view-by-view decorators.
- Keep login, registration, password-reset flows, Django admin authentication, and static assets reachable while signed out.
- Preserve the requested destination through the normal `next` login parameter.
- Keep authenticated behavior and all existing per-video/channel visibility rules unchanged.
- Gate local `/media/` requests while signed out; existing protected video-file and storage authorization remain authoritative.
- Add focused regression tests and environment documentation.

## Commercial rationale

Many SMB training/client/internal-content use cases need a private portal before they need advanced monetization. An opt-in site gate makes the existing application credible for those pilots without forking routes, adding a new identity provider, or paying for infrastructure.

## Acceptance criteria

1. Private portal mode is disabled by default.
2. With the mode enabled, anonymous application requests redirect to login with a safe `next` destination.
3. Authenticated users retain normal access.
4. Login, registration, password-reset, admin login, and static assets remain reachable anonymously.
5. Direct local media requests are not exempted from the private gate.
6. Existing authorization/visibility rules remain in force after login.
7. No migration, dependency, paid service, live-payment, or AWS resource change is introduced.

## Security note

This is a Django request-layer access gate, not a replacement for object/storage authorization. Protected video files continue to use the existing access view. External object-storage URLs remain governed by the existing signed/private storage configuration.

## Verification

    python manage.py check
    python manage.py makemigrations --check --dry-run
    python manage.py test video.test_private_portal
    python manage.py test --parallel 4
    docker compose config --quiet

## Out of scope

- Disabling public registration
- SSO/SAML/OIDC
- Customer-specific invitation-only onboarding
- Per-tenant portals
- Custom domains
- Storage-policy redesign

## Delivered

- Added `DJANGO_PRIVATE_PORTAL=false` with public behavior unchanged by default.
- Added a middleware-level login gate immediately after Django authentication.
- Anonymous application requests preserve their requested destination through the normal `next` parameter.
- Login, registration, password-reset routes, Django admin authentication, and static assets remain reachable while signed out.
- Local `/media/` requests are not exempted from the private gate.
- Existing per-object visibility and protected video-file authorization remain unchanged after login.
- Added focused regression coverage for default/public mode, redirects, query-string preservation, authenticated access, public exceptions, static assets, and media gating.

## Verification results

- `git diff --check` passed locally.
- `python3 -m compileall -q video yt` passed locally.
- GitHub Actions Django checks run #627 passed configuration and migration-drift checks and all 916 tests with one expected skip.
- Local Docker focused tests were attempted, but the host Docker daemon stalled before test-container creation; no local Docker test success is claimed for this sprint.
