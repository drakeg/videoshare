# Pilot User Access-State Controls Sprint

## Goal

Let staff suspend/reactivate ordinary pilot users directly from the filtered Pilot Users directory while preserving moderation safeguards, audit history, and directory return state.

## Scope

- Add a staff-only POST action dedicated to Pilot Users.
- Restrict targets to ordinary non-staff, non-superuser accounts.
- Reuse the existing audited `set_user_active` moderation service.
- Require an operator-provided moderation reason for both suspend and reactivate.
- Show Suspend on active pilot users and Reactivate on suspended pilot users.
- Preserve bounded search, account-status, onboarding-status, and current page on return.
- Validate return-state values instead of accepting an arbitrary redirect URL.
- Keep password setup/reset, setup email, CSV import, and user privileges unchanged.

## Commercial rationale

Operators managing a closed pilot should not have to leave the Pilot Users directory for routine reversible access changes. Reusing the existing audited moderation service keeps the workflow convenient without weakening safeguards.

## Acceptance criteria

1. Staff can suspend an active ordinary pilot user from the directory.
2. Staff can reactivate a suspended ordinary pilot user from the directory.
3. A non-empty moderation reason is required.
4. Every successful state change creates the existing moderation audit event.
5. Staff, superuser, and non-existent targets are rejected by the pilot-specific action.
6. Nonstaff callers remain blocked.
7. Search/status/onboarding/page state is preserved after the POST.
8. Invalid return-state values are normalized safely.
9. Existing reset/setup actions remain unavailable while suspended and return after reactivation.
10. Focused tests cover permissions, audit events, reason validation, state changes, and safe return state.
11. No migration, dependency, paid service, live payment, or AWS resource change is introduced.

## Verification

    python manage.py test video.test_pilot_user_access_state
    python manage.py test --parallel 4
    docker compose config --quiet

## Out of scope

- Bulk suspend/reactivate
- Account deletion
- Staff/superuser state management
- Automatic inactivity policies

## Delivered

- Added a staff-only ordinary-user suspend/reactivate POST action for Pilot Users.
- Reused the existing audited `set_user_active` moderation service.
- Required a moderation reason for both state transitions.
- Added in-directory Suspend / Reactivate controls.
- Preserved bounded search, account-status, onboarding-status, and page return state through validated parameters.
- Restricted targets to non-staff, non-superuser ordinary accounts.
- Preserved suspended-user reset/setup guidance and action boundaries.

## Verification results

- `python3 -m compileall -q video` passed locally.
- `git diff --check` passed locally.
- `docker compose config --quiet` passed locally.
- Focused local Docker execution stalled at host-daemon container creation and was terminated; no local focused pass is claimed.
- GitHub Actions Django checks run #674 passed configuration and migration-drift checks and all 1012 tests with one expected skip.
- Repository standards workflow run #36 passed.
