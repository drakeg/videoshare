# Configurable Site Branding Sprint

## Goal

Make VideoShare demo/pilot deployments brandable for SMB prospects without editing application code or changing data models.

## Scope

- Add one environment-driven site-name setting with `VideoShare` as the default.
- Expose the site name through a global template context processor.
- Replace hardcoded `VideoShare` copy in shared navigation, page titles, search placeholders, auth pages, empty states, and monetization templates.
- Document the setting in `.env.example`.
- Preserve all existing behavior when no custom site name is configured.
- Add regression tests for default and customized branding.

## Commercial rationale

A generic hardcoded product name makes every pilot look like a developer demo. Environment-driven branding lets the same build present a customer's name immediately, improving demo credibility without adding a schema, admin UI, paid service, or deployment dependency.

## Acceptance criteria

1. `DJANGO_SITE_NAME` controls the visible site name.
2. Blank or missing configuration falls back to `VideoShare`.
3. Shared header branding, page titles, and search placeholders use the configured name.
4. User-facing hardcoded `VideoShare` references in application templates are removed or intentionally retained only where they refer to the project itself.
5. Existing routes and authorization behavior remain unchanged.
6. No migration, dependency, paid service, live-payment, or AWS resource change is introduced.

## Verification

    python manage.py check
    python manage.py makemigrations --check --dry-run
    python manage.py test video.test_site_branding video.test_ui_design
    python manage.py test --parallel 4
    docker compose config --quiet

## Out of scope

- Uploaded custom logos/favicons
- Per-channel branding
- Custom domains
- Theme/color editing
- White-label removal of all product attribution

## Delivered

- Added `DJANGO_SITE_NAME` with `VideoShare` as the default and blank-value fallback.
- Added a global template context processor for site branding.
- Replaced hardcoded product-name copy across shared navigation, page titles, search placeholders, authentication pages, channel/playlist defaults, creator/viewer surfaces, and monetization templates.
- Documented the environment setting in `.env.example`.
- Added regression tests for the default brand and an SMB-specific custom brand.

## Verification results

- `git diff --check` passed locally.
- `python3 -m compileall -q video monetization yt` passed locally.
- GitHub Actions Django checks run #625 passed configuration and migration-drift checks and all 912 tests with one expected skip.
- Local Docker focused tests were attempted twice, but the host Docker daemon stalled at container creation; no local Docker test success is claimed for this sprint.
