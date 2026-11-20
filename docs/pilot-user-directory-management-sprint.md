# Pilot User Directory Management Sprint

## Goal

Make larger closed-pilot cohorts manageable after bulk import by adding bounded search, account-status filtering, and pagination to the staff-only Pilot Users directory.

## Scope

- Search ordinary pilot users by username, email, first name, or last name.
- Bound normalized search input to 100 characters.
- Filter by All, Active, or Suspended account state.
- Validate filter values and fall back safely to All.
- Paginate results at 50 users per page.
- Preserve search/filter state across pager links.
- Reset stale page state when a new search/filter form is submitted.
- Keep provisioning, reset/setup links, email delivery, bulk import, moderation, and privilege boundaries unchanged.
- Add focused regression coverage.

## Commercial rationale

Bulk import supports cohorts up to 200 users, but the current Pilot Users page only exposes the latest 50. Search/filter/pagination closes that immediate operator-support gap without adding infrastructure or changing account semantics.

## Acceptance criteria

1. Staff can search username/email/first/last name case-insensitively.
2. Search input is trimmed and capped at 100 characters.
3. Staff can filter All/Active/Suspended.
4. Invalid status values safely fall back to All.
5. Results are paginated at 50 per page.
6. Search/filter parameters are preserved in pagination links.
7. A new search/filter submission does not carry a stale page number.
8. Existing provisioning/reset/email/import actions remain available on matching rows.
9. Nonstaff access remains blocked.
10. Focused tests cover search, filters, fallback, pagination, and state preservation.
11. No migration, dependency, paid service, live payment, or AWS resource change is introduced.

## Verification

    python manage.py test video.test_pilot_user_directory
    python manage.py test --parallel 4
    docker compose config --quiet

## Out of scope

- Account deletion
- Bulk suspension/reactivation
- Additional roles/permissions
- Exporting the full user directory

## Delivered

- Added bounded case-insensitive search across username, email, first name, and last name.
- Added validated All / Active / Suspended filtering with safe fallback.
- Added 50-user pagination with search/filter state preserved in pager links.
- New filter submissions reset stale page state.
- Existing provisioning, reset/setup, email, CSV import, and privilege boundaries remain unchanged.

## Verification results

- `python3 -m compileall -q video` passed locally.
- `git diff --check` passed locally.
- `docker compose config --quiet` passed locally.
- The focused local Docker invocation stalled before test output and was terminated; no local focused pass is claimed.
- GitHub Actions Django checks run #669 passed configuration and migration-drift checks and all 999 tests with one expected skip.
- Repository standards workflow run #31 passed.
