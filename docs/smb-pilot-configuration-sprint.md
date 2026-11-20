# SMB Pilot Configuration Sprint

## Goal

Consolidate the customer-facing pilot configuration work into one reviewable change: configurable site branding plus optional public-registration shutdown, on top of the already-merged private portal mode.

## Scope

- Add `DJANGO_SITE_NAME` with `VideoShare` as the default.
- Replace hardcoded product-name copy across user-facing templates.
- Add `DJANGO_ALLOW_PUBLIC_REGISTRATION=true` with existing signup behavior unchanged by default.
- Hide signup links and block registration GET/POST with HTTP 403 when disabled.
- Preserve existing-user login, password reset, admin provisioning, private-portal behavior, visibility rules, and media authorization.
- Keep all configuration environment-driven; no schema or paid-service changes.

## Commercial rationale

This gives an SMB pilot three complementary deployment controls: customer-facing naming, optional login-required portal mode (already merged), and optional closed registration. Together they make a credible branded/private pilot without custom code per customer.

## Acceptance criteria

1. Missing/blank site name falls back to VideoShare.
2. Shared branding, titles, search placeholders, auth pages, and default channel/playlist copy use the configured site name.
3. Public registration remains enabled by default.
4. Disabled registration returns HTTP 403 for GET/POST and creates no account.
5. Signup links disappear when registration is disabled.
6. Existing users still log in and password reset/admin provisioning remain unchanged.
7. Private portal mode remains functional and independent.
8. No migration, dependency, paid service, live-payment, or AWS resource change.

## Verification

    python manage.py check
    python manage.py makemigrations --check --dry-run
    python manage.py test video.test_site_branding video.test_registration_control video.test_registration video.test_private_portal
    python manage.py test --parallel 4
    docker compose config --quiet

## Out of scope

- Uploaded logos/favicons
- Custom domains
- SSO/SAML/OIDC
- Invitation-only onboarding
- Per-tenant settings

## Delivered

- Added `DJANGO_SITE_NAME` with `VideoShare` fallback.
- Applied the configured site name across shared navigation, page titles, search placeholders, auth pages, and customer-facing template copy.
- Added `DJANGO_ALLOW_PUBLIC_REGISTRATION=true` with existing signup behavior unchanged by default.
- Disabled registration GET/POST requests return HTTP 403 and do not create users.
- Signup links are hidden when public registration is disabled.
- Existing-user login, password reset, admin provisioning, private portal behavior, visibility rules, and media authorization remain intact.
- Consolidated the overlapping work from PRs #282 and #284 onto current `main`.

## Verification results

- `git diff --check` passed locally.
- `python3 -m compileall -q video monetization yt` passed locally.
- `docker compose config --quiet` passed locally.
- GitHub Actions Django checks run #637 passed configuration and migration-drift checks and all 925 tests with one expected skip.
