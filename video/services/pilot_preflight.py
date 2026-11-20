from dataclasses import dataclass


@dataclass(frozen=True)
class PilotCheckResult:
    status: str
    code: str
    message: str
    guidance: str


def _result(status, code, message, guidance):
    return PilotCheckResult(status=status, code=code, message=message, guidance=guidance)


def run_pilot_preflight(settings_obj, *, profile="public", deployment=False):
    if profile not in {"public", "private"}:
        raise ValueError("profile must be 'public' or 'private'")

    results = []

    secret_key = str(getattr(settings_obj, "SECRET_KEY", "") or "")
    if not secret_key or secret_key == "replace-with-a-long-random-secret":
        results.append(
            _result(
                "FAIL",
                "secret-key",
                "The deployment is using a missing or example Django secret key.",
                "Set DJANGO_SECRET_KEY to a unique long random value.",
            )
        )
    else:
        results.append(
            _result(
                "PASS",
                "secret-key",
                "Django secret key is set and is not the committed example value.",
                "Keep DJANGO_SECRET_KEY private and unique per deployment.",
            )
        )

    allowed_hosts = list(getattr(settings_obj, "ALLOWED_HOSTS", []) or [])
    if "*" in allowed_hosts:
        results.append(
            _result(
                "FAIL",
                "allowed-hosts",
                "DJANGO_ALLOWED_HOSTS contains a wildcard.",
                "Replace * with the exact hostnames/IP addresses used by this deployment.",
            )
        )
    elif not allowed_hosts:
        results.append(
            _result(
                "FAIL",
                "allowed-hosts",
                "No allowed hosts are configured.",
                "Set DJANGO_ALLOWED_HOSTS to the exact hostnames/IP addresses used by this deployment.",
            )
        )
    else:
        results.append(
            _result(
                "PASS",
                "allowed-hosts",
                "Allowed hosts are explicitly scoped.",
                "Keep DJANGO_ALLOWED_HOSTS limited to hosts the deployment actually uses.",
            )
        )

    site_name = str(getattr(settings_obj, "SITE_NAME", "") or "").strip()
    if not site_name or site_name == "VideoShare":
        results.append(
            _result(
                "WARN",
                "site-brand",
                "The deployment still uses the default VideoShare site name.",
                "Set DJANGO_SITE_NAME to the customer-facing pilot brand before a branded demo.",
            )
        )
    else:
        results.append(
            _result(
                "PASS",
                "site-brand",
                f"Customer-facing site name is configured as {site_name!r}.",
                "Confirm the displayed brand with the pilot customer before launch.",
            )
        )

    private_portal = bool(getattr(settings_obj, "PRIVATE_PORTAL", False))
    public_registration = bool(getattr(settings_obj, "ALLOW_PUBLIC_REGISTRATION", True))

    if profile == "private":
        if private_portal:
            results.append(
                _result(
                    "PASS",
                    "private-portal",
                    "Private portal mode is enabled.",
                    "Keep DJANGO_PRIVATE_PORTAL=true for a login-required pilot.",
                )
            )
        else:
            results.append(
                _result(
                    "FAIL",
                    "private-portal",
                    "Private profile selected but private portal mode is disabled.",
                    "Set DJANGO_PRIVATE_PORTAL=true.",
                )
            )

        if public_registration:
            results.append(
                _result(
                    "FAIL",
                    "public-registration",
                    "Private profile selected but anonymous public registration is enabled.",
                    "Set DJANGO_ALLOW_PUBLIC_REGISTRATION=false and provision pilot users intentionally.",
                )
            )
        else:
            results.append(
                _result(
                    "PASS",
                    "public-registration",
                    "Public self-registration is disabled for the private pilot.",
                    "Provision users through the approved operator/admin workflow.",
                )
            )
    else:
        results.append(
            _result(
                "PASS",
                "access-profile",
                "Public pilot profile selected.",
                "Use --profile private for a login-required customer portal check.",
            )
        )

    debug = bool(getattr(settings_obj, "DEBUG", False))
    if deployment and debug:
        results.append(
            _result(
                "FAIL",
                "debug",
                "Deployment mode requires Django debug mode to be disabled.",
                "Set DJANGO_DEBUG=false.",
            )
        )
    elif debug:
        results.append(
            _result(
                "WARN",
                "debug",
                "Django debug mode is enabled.",
                "This is acceptable for trusted local demos only; use --deployment before an internet-facing pilot.",
            )
        )
    else:
        results.append(
            _result(
                "PASS",
                "debug",
                "Django debug mode is disabled.",
                "Keep DJANGO_DEBUG=false outside trusted local development.",
            )
        )

    if deployment:
        deployment_requirements = (
            (
                "ssl-redirect",
                bool(getattr(settings_obj, "SECURE_SSL_REDIRECT", False)),
                "HTTPS redirect is enabled.",
                "HTTPS redirect is disabled.",
                "Set DJANGO_SECURE_SSL_REDIRECT=true after TLS is configured.",
            ),
            (
                "session-cookie",
                bool(getattr(settings_obj, "SESSION_COOKIE_SECURE", False)),
                "Session cookies require HTTPS.",
                "Session cookies are not marked secure.",
                "Set DJANGO_SESSION_COOKIE_SECURE=true.",
            ),
            (
                "csrf-cookie",
                bool(getattr(settings_obj, "CSRF_COOKIE_SECURE", False)),
                "CSRF cookies require HTTPS.",
                "CSRF cookies are not marked secure.",
                "Set DJANGO_CSRF_COOKIE_SECURE=true.",
            ),
        )
        for code, enabled, ok_message, fail_message, guidance in deployment_requirements:
            results.append(
                _result(
                    "PASS" if enabled else "FAIL",
                    code,
                    ok_message if enabled else fail_message,
                    guidance,
                )
            )

    provider = str(getattr(settings_obj, "MONETIZATION_PAYMENT_PROVIDER", "sandbox") or "").lower()
    secret = str(getattr(settings_obj, "STRIPE_SECRET_KEY", "") or "")
    if provider == "stripe" and secret.startswith("sk_test_"):
        results.append(
            _result(
                "PASS",
                "payments",
                "Stripe provider is configured with a test-mode secret key.",
                "Keep live Stripe activation disabled until explicitly authorized.",
            )
        )
    elif provider == "stripe":
        results.append(
            _result(
                "WARN",
                "payments",
                "Stripe provider is selected without a test-mode secret key.",
                "Use MONETIZATION_PAYMENT_PROVIDER=sandbox or configure Stripe test-mode credentials.",
            )
        )
    else:
        results.append(
            _result(
                "PASS",
                "payments",
                "Monetization remains on the sandbox/non-live provider path.",
                "Do not enable live payments without explicit authorization.",
            )
        )

    return results
