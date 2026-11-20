# Existing Pilot User Reset Link Sprint

## Goal

Let trusted staff generate a secure password reset/setup link for an existing active ordinary pilot user directly from the branded Pilot Users workflow.

## Scope

- Add a staff-only POST action on each eligible Pilot Users row.
- Generate a fresh Django password-reset token URL for the selected active non-staff/non-superuser account.
- Return to the Pilot Users page and display the generated link with clear security guidance.
- Do not change the user's current password, role, email, activation state, or other account data.
- Do not allow the custom action for staff, superusers, or inactive users.
- Keep public registration and private portal settings unchanged.
- Add regression coverage for permissions, eligible/ineligible accounts, token validity, and non-mutation of existing passwords.

## Commercial rationale

Operators often need to recover onboarding when a setup link was lost or help an existing user reset access. Requiring Django admin or email-backend troubleshooting adds avoidable support friction during a pilot.

## Acceptance criteria

1. Staff see a "Generate reset link" action for active ordinary users.
2. The action is POST-only and CSRF-protected.
3. Anonymous/non-staff users cannot invoke it.
4. Staff/superuser/inactive targets are rejected.
5. The generated URL reaches the branded password-reset-confirm flow.
6. Generating a link does not change the target's existing password hash, role, activation state, or email.
7. A user can set a new password through the generated link and log in.
8. The Pilot Users page clearly warns that reset links are sensitive and may remain valid until used/expired.
9. Focused tests cover the action and security boundaries.
10. No migration, dependency, paid service, live-payment, or AWS resource change is introduced.

## Security note

Generating a new Django reset token does not revoke older still-valid reset tokens by itself. Existing tokens become invalid when the user's password changes, last-login state changes, relevant account data changes, or Django's reset timeout expires.

## Verification

    python manage.py test video.test_pilot_user_reset_links
    python manage.py test --parallel 4
    docker compose config --quiet

## Delivered

- Added a staff-only, POST-only reset/setup-link action from Pilot Users.
- Restricted the custom action to active ordinary users; inactive/staff/superuser targets are rejected.
- Added reset/setup link output to the existing branded Pilot Users page.
- Added clear guidance that generating a token does not mutate the existing password and does not revoke older valid tokens by itself.
- Suspended users show **Reactivate first** rather than a reset action.
- Added end-to-end regression coverage proving the existing password hash/role/account state remain unchanged until the target user completes the reset.

## Verification results

- Focused Docker pilot-user lifecycle suite passed 14/14 in 10.194s.
- `python3 -m compileall -q video` passed locally.
- `git diff --check` passed locally.
- `docker compose config --quiet` passed locally.
- GitHub Actions Django checks run #662 passed configuration and migration-drift checks and all 968 tests with one expected skip.
- Repository standards workflow run #24 passed.
