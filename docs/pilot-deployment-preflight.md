# SMB Pilot Deployment Preflight

Use the read-only `pilot_check` management command before an SMB demo, pilot handoff, or internet-facing deployment.

The command does **not** change configuration, create users, provision infrastructure, or enable payments. It only evaluates the active Django settings and reports PASS/WARN/FAIL results with the environment variable to change.

## Public pilot

For a normal public-facing VideoShare deployment:

```bash
docker compose run --rm --entrypoint python test manage.py pilot_check --profile public
```

The public profile verifies the secret key, explicit allowed hosts, customer-facing site name, debug state, and payment-provider safety. A local development configuration may complete with warnings, such as debug mode or the default VideoShare brand.

## Private pilot

For a login-required customer portal:

```bash
docker compose run --rm --entrypoint python test manage.py pilot_check --profile private
```

The private profile additionally requires:

- `DJANGO_PRIVATE_PORTAL=true`
- `DJANGO_ALLOW_PUBLIC_REGISTRATION=false`

This confirms the portal is login-gated and anonymous visitors cannot self-register. It does not replace existing per-video/channel visibility or protected-media authorization.

When public registration is disabled, trusted staff can provision ordinary users from **Site Administration → Pilot users** and share the generated password-setup link. See `docs/pilot-user-provisioning.md`.

## Internet-facing deployment hardening

After TLS is configured, add `--deployment`:

```bash
docker compose run --rm --entrypoint python test manage.py pilot_check --profile private --deployment
```

Deployment mode requires:

- `DJANGO_DEBUG=false`
- `DJANGO_SECURE_SSL_REDIRECT=true`
- `DJANGO_SESSION_COOKIE_SECURE=true`
- `DJANGO_CSRF_COOKIE_SECURE=true`

It also retains all normal pilot checks.

## Result meanings

- **PASS** — the checked setting matches the selected profile.
- **WARN** — the application can continue, but the item should be reviewed before a customer demo.
- **FAIL** — the command exits non-zero. Resolve the reported configuration before treating the pilot as ready.

The command always fails when `DJANGO_ALLOWED_HOSTS` contains `*` or when the committed example `DJANGO_SECRET_KEY` is still in use.

## Payment boundary

The preflight accepts the built-in sandbox provider and Stripe **test-mode** credentials. It does not authorize or enable live Stripe processing. Existing safeguards continue to reject live Stripe secret keys.

## Typical private pilot configuration

```text
DJANGO_SITE_NAME=Acme Training TV
DJANGO_PRIVATE_PORTAL=true
DJANGO_ALLOW_PUBLIC_REGISTRATION=false
DJANGO_DEBUG=false

DJANGO_ALLOWED_HOSTS=pilot.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://pilot.example.com

DJANGO_SECURE_SSL_REDIRECT=true
DJANGO_SESSION_COOKIE_SECURE=true
DJANGO_CSRF_COOKIE_SECURE=true
```

Use deployment-specific secrets and hostnames rather than copying example values literally.
