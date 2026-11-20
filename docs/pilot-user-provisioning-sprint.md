# Closed Pilot User Provisioning Sprint

## Goal

Give trusted staff a safe, branded workflow for provisioning closed-pilot users when public registration is disabled, without distributing temporary passwords or requiring direct Django-admin navigation.

## Scope

- Add a staff-only Pilot Users page under the existing Site Administration area.
- List recently provisioned/active users with clear status.
- Add a focused form to create a normal non-staff account from username, email, first name, and last name.
- Generate a password-setup URL using Django's password-reset token flow.
- Never display, store, or email a temporary plaintext password.
- Add the missing password-reset templates so both "Lost password?" and operator-generated password-setup links render end to end.
- Keep staff/superuser creation out of the custom workflow; elevated accounts remain a Django-admin responsibility.
- Preserve public-registration, private-portal, moderation, and authentication settings.

## Commercial rationale

Closed pilots need operator-controlled account creation. Requiring operators to fall back to raw Django admin or invent temporary passwords increases onboarding/support effort and makes a branded pilot feel unfinished.

## Acceptance criteria

1. Only staff can access the Pilot Users page.
2. Staff can create a non-staff, active user with a unique username/email.
3. Duplicate username/email submissions show validation errors and create no extra user.
4. Created users receive a random internal password hash unknown to the operator; the page exposes only a one-time password-setup URL.
5. The setup URL successfully reaches Django's password-reset-confirm flow and allows the user to choose a password.
6. The custom workflow cannot create staff or superusers.
7. Existing users remain unchanged.
8. Standard password-reset request/done/confirm/complete pages render with the shared site branding.
9. Site Administration links to Pilot Users.
10. Focused tests cover permissions, provisioning, duplicate validation, setup token validity, and password-reset templates.
11. No migration, runtime dependency, paid service, live-payment, or AWS resource change is introduced.

## Security boundaries

- Password-setup links contain Django's signed reset token and should be treated as secrets until used or expired.
- The custom workflow creates only ordinary users.
- Staff/superuser provisioning remains in Django admin.
- No email is sent automatically in this sprint; operators can deliver the setup link through their approved channel.

## Verification

    python manage.py check
    python manage.py makemigrations --check --dry-run
    python manage.py test video.test_pilot_user_provisioning
    python manage.py test --parallel 4
    docker compose config --quiet

## Out of scope

- Bulk CSV import
- Invitation email delivery
- Expiring custom invitation models
- SSO/SAML/OIDC
- Role/group administration
- Staff/superuser creation

## Delivered

- Added a staff-only **Site Administration → Pilot users** page.
- Added ordinary-user provisioning with case-insensitive duplicate username/email validation.
- Provisioned users are always active, non-staff, and non-superusers.
- Temporary plaintext passwords are never displayed or emailed; a random internal password is set and the operator receives a signed password-setup URL instead.
- Added branded password-reset form/done/confirm/complete/email templates and explicitly bound auth reset routes to unique app templates so Django admin templates cannot override them.
- Added Site Administration navigation plus operator documentation in `docs/pilot-user-provisioning.md`.
- Extended the accessibility regression gate to the Pilot Users page and password-reset entry pages.

## Verification results

- Focused Docker provisioning/accessibility suite passed 15/15 in 6.773s.
- `python3 -m compileall -q video yt` passed locally.
- `git diff --check` passed locally.
- `docker compose config --quiet` passed locally.
- GitHub Actions Django checks run #660 passed configuration and migration-drift checks and all 961 tests with one expected skip.
- Repository standards workflow run #22 passed.
