# Filtered Pilot User Directory Export Sprint

## Goal

Let staff download the currently filtered Pilot Users directory for operator records without exporting passwords, setup/reset tokens, or other secret material.

## Scope

- Add a staff-only CSV export route for ordinary pilot users.
- Apply the same bounded search, account-status, and onboarding-status filters as the directory.
- Export all matching users, independent of the current UI page.
- Include only operational fields: username, email, first/last name, active/suspended state, last successful sign-in, and joined timestamp.
- Never export password hashes, setup/reset URLs/tokens, staff/superuser accounts, or moderation reasons.
- Neutralize spreadsheet-formula prefixes in user-controlled text cells.
- Add an Export CSV action that preserves the current directory filters.
- Add focused regression coverage for permissions, filters, sensitive-field exclusion, and formula neutralization.

## Commercial rationale

SMB operators often need a simple roster/status file for pilot coordination. A filtered export reduces manual copying while keeping sensitive authentication material out of the download.

## Acceptance criteria

1. Only staff can download the export.
2. Staff/superuser accounts are excluded.
3. Search/account/onboarding filters match the directory semantics.
4. Export ignores UI pagination and includes every matching ordinary user.
5. CSV contains only approved operational columns.
6. Password hashes and setup/reset tokens never appear.
7. Formula-like user text is neutralized for spreadsheet safety.
8. Last-login and joined timestamps are deterministic ISO-8601 values.
9. The directory export link preserves current filter state.
10. Focused tests cover permissions, filtering, full-match export, headers, sensitive-field exclusion, and spreadsheet safety.
11. No migration, dependency, paid service, live payment, or AWS resource change is introduced.

## Verification

    python manage.py test video.test_pilot_user_directory_export
    python manage.py test --parallel 4
    docker compose config --quiet

## Out of scope

- Setup-link CSV export for existing users
- Bulk email
- Import/export synchronization
- Background export jobs

## Delivered

- Added a staff-only filtered Pilot Users CSV export.
- Reused the exact directory search/account/onboarding filter semantics.
- Exported all matching ordinary users independent of UI pagination.
- Limited columns to operational identity/status/timestamp fields.
- Excluded staff/superusers, password hashes, setup/reset URLs/tokens, and moderation reasons.
- Neutralized spreadsheet-formula prefixes in user-controlled text cells.
- Added an Export CSV action that preserves current filters.

## Verification results

- `python3 -m compileall -q video` passed locally.
- `git diff --check` passed locally.
- `docker compose config --quiet` passed locally.
- GitHub Actions Django checks run #676 passed configuration and migration-drift checks and all 1018 tests with one expected skip.
- Repository standards workflow run #38 passed.
