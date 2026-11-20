# Pilot Onboarding Status Visibility Sprint

## Goal

Help staff identify pilot users who have never successfully signed in after provisioning so setup assistance can be targeted without adding a new account-state model.

## Scope

- Display each pilot user's last successful sign-in in the Pilot Users directory.
- Show a clear "Never signed in" state when `last_login` is null.
- Add an onboarding filter: All / Never signed in / Has signed in.
- Preserve onboarding filter state across pagination alongside search/account-status filters.
- Validate onboarding filter values and fall back safely to All.
- Keep account provisioning, password setup/reset, email delivery, CSV import, suspension state, and privilege boundaries unchanged.
- Do not interpret `last_login` as proof that a particular setup email was delivered/read.

## Commercial rationale

After provisioning a cohort, operators need a low-cost way to identify who likely still needs access help. Django already records successful authentication in `last_login`, so this provides useful support visibility without adding schema, tracking pixels, provider-specific delivery telemetry, or privacy-invasive monitoring.

## Acceptance criteria

1. The directory shows "Never signed in" for users with no successful login.
2. Users with a `last_login` timestamp show that timestamp.
3. Staff can filter All / Never signed in / Has signed in.
4. Invalid onboarding-filter values safely fall back to All.
5. Search, account-status, onboarding-status, and pagination compose correctly.
6. Pager links preserve all active directory filters.
7. The UI wording does not claim email delivery/read status or password-setup completion.
8. Nonstaff access remains blocked.
9. Focused tests cover display, filters, fallback, and composed filtering.
10. No migration, dependency, paid service, live payment, or AWS resource change is introduced.

## Verification

    python manage.py test video.test_pilot_user_onboarding_status
    python manage.py test --parallel 4
    docker compose config --quiet

## Out of scope

- Email delivery/open tracking
- Password-setup completion tracking separate from successful login
- New account-state models
- Automated reminders

## Delivered

- Added last-successful-sign-in visibility to the Pilot Users directory.
- Added explicit `Never signed in` display for users whose Django `last_login` is null.
- Added validated All / Never signed in / Has signed in filtering.
- Composed onboarding status with existing search and Active/Suspended filters.
- Preserved onboarding/search/account state across pagination.
- Kept wording limited to successful sign-in state; no email-read or password-setup completion claim is made.

## Verification results

- `python3 -m compileall -q video` passed locally.
- `git diff --check` passed locally.
- `docker compose config --quiet` passed locally.
- GitHub Actions Django checks run #671 passed configuration and migration-drift checks and all 1004 tests with one expected skip.
- Repository standards workflow run #33 passed.
