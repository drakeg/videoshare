# Optional Pilot-User Setup Email Sprint

## Goal

Reduce manual setup-link delivery for closed pilots while preserving provider independence, manual-link fallback, and opt-in email behavior.

## Scope

- Add `DJANGO_PILOT_USER_SETUP_EMAIL_ENABLED=false`.
- Reuse Django's configured email backend and `DJANGO_DEFAULT_FROM_EMAIL`.
- Add a service for branded setup/reset-link email delivery.
- Use `DJANGO_SITE_NAME` in email subject/body.
- Let staff optionally email a setup link immediately after creating one pilot user.
- Let staff email a reset/setup link for an existing active ordinary user.
- Preserve the generated manual setup/reset URL in the UI whether email succeeds or fails.
- Do not expose email exception details to the browser.
- Do not send anything when the feature flag is disabled.
- Do not add SMTP/provider dependencies.

## Commercial rationale

Manual link copying is reasonable for a tiny pilot but becomes repetitive and error-prone. Optional provider-agnostic email delivery reduces operator effort while keeping the default deployment free, local, and safe.

## Acceptance criteria

1. Email delivery is disabled by default.
2. When enabled, a staff operator can choose to email a new user's setup link.
3. When enabled, staff can email an existing active ordinary user's reset/setup link.
4. Email uses the configured site name and from address.
5. The setup/reset URL is still displayed as manual fallback.
6. Missing recipient email prevents sending and preserves the manual-link workflow.
7. Backend exceptions are handled without rolling back user creation or changing passwords.
8. Staff/superuser targets remain ineligible for the pilot reset-link workflow.
9. Bulk CSV import behavior remains unchanged and does not automatically send email.
10. Focused tests cover disabled/enabled delivery, missing email, backend failure, branding, and account-state safety.
11. No migration, runtime dependency, paid service, live payment, or AWS resource change is introduced.

## Verification

    python manage.py test video.test_pilot_user_setup_email
    python manage.py test --parallel 4
    docker compose config --quiet

## Out of scope

- Bulk email delivery for CSV imports
- Email tracking/read receipts
- Provider-specific APIs
- HTML email templates
- Forced first-login password rotation

## Delivered

- Added `DJANGO_PILOT_USER_SETUP_EMAIL_ENABLED=false`.
- Reused Django's configured email backend and `DJANGO_DEFAULT_FROM_EMAIL`.
- Added branded setup/reset email delivery using `DJANGO_SITE_NAME`.
- Added opt-in email delivery for newly provisioned individual pilot users.
- Added staff-triggered reset/setup email delivery for existing active ordinary users.
- Preserved the manual signed URL on success, missing-email, disabled, and backend-failure paths.
- Kept bulk CSV imports non-delivery-only so cohort provisioning cannot enter ambiguous partial-email state.
- Extended `pilot_check` to warn when setup email is enabled with console/locmem/dummy backends.
- Added operator documentation for backend configuration and fallback behavior.

## Verification results

- Focused setup-email + preflight Docker tests passed 23/23.
- Accessibility regression Docker tests passed 8/8.
- `python3 -m compileall -q video yt` passed locally.
- `git diff --check` passed locally.
- `docker compose config --quiet` passed locally.
- GitHub Actions Django checks run #666 passed configuration and migration-drift checks and all 990 tests with one expected skip.
- Repository standards workflow run #28 passed.
- A full local Docker run started successfully with four cloned test databases, confirming parallel execution, and progressed without a reported test failure; the remote shell ended with exit 130 before Django emitted a final summary, so no full-local pass is claimed.
