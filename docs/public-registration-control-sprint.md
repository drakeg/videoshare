# Public Registration Control Sprint

## Goal

Let SMB/private-portal deployments disable public self-signup while preserving the existing public-registration behavior by default.

## Scope

- Add `DJANGO_ALLOW_PUBLIC_REGISTRATION=true` as the default.
- Replace the always-on registration view with a configuration-aware registration view.
- Return a clear forbidden response when registration is disabled.
- Hide public Sign up links from anonymous navigation and the login page when registration is disabled.
- Expose registration availability through a global template context processor.
- Keep admin-created/existing users and login/password-reset flows unchanged.
- Add focused regression coverage and environment documentation.

## Commercial rationale

A login-required portal is not meaningfully closed if any visitor can still self-register. Registration control lets an SMB pilot restrict access to users provisioned by the operator/admin without adding SSO or invitation infrastructure.

## Acceptance criteria

1. Public registration remains enabled by default.
2. With registration disabled, GET and POST to the registration route return HTTP 403 and create no user.
3. Sign up links are hidden from the shared anonymous navigation and login page when disabled.
4. Existing users can still log in normally.
5. Password-reset and Django admin user provisioning remain unchanged.
6. No migration, dependency, paid service, live-payment, or AWS resource change is introduced.

## Verification

    python manage.py check
    python manage.py makemigrations --check --dry-run
    python manage.py test video.test_registration_control video.test_registration
    python manage.py test --parallel 4
    docker compose config --quiet

## Out of scope

- Invitation-only registration
- Email allowlists/domain restrictions
- SSO/SAML/OIDC
- Admin bulk user import
- Per-tenant registration policy
