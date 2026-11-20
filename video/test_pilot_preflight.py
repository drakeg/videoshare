from io import StringIO
from types import SimpleNamespace

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, override_settings

from .services.pilot_preflight import run_pilot_preflight


def make_settings(**overrides):
    values = {
        "SECRET_KEY": "a-unique-secret-key-that-is-long-enough-for-tests",
        "ALLOWED_HOSTS": ["localhost", "pilot.example.test"],
        "SITE_NAME": "Acme Training TV",
        "PRIVATE_PORTAL": False,
        "ALLOW_PUBLIC_REGISTRATION": True,
        "DEBUG": True,
        "SECURE_SSL_REDIRECT": False,
        "SESSION_COOKIE_SECURE": False,
        "CSRF_COOKIE_SECURE": False,
        "MONETIZATION_PAYMENT_PROVIDER": "sandbox",
        "STRIPE_SECRET_KEY": "",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class PilotPreflightServiceTests(SimpleTestCase):
    def statuses(self, results):
        return {result.code: result.status for result in results}

    def test_public_local_profile_has_no_failures_for_safe_local_configuration(self):
        results = run_pilot_preflight(make_settings(), profile="public")

        self.assertNotIn("FAIL", [result.status for result in results])
        self.assertEqual(self.statuses(results)["debug"], "WARN")
        self.assertEqual(self.statuses(results)["access-profile"], "PASS")

    def test_private_profile_requires_private_portal_and_closed_registration(self):
        results = run_pilot_preflight(make_settings(), profile="private")
        statuses = self.statuses(results)

        self.assertEqual(statuses["private-portal"], "FAIL")
        self.assertEqual(statuses["public-registration"], "FAIL")

    def test_private_profile_passes_access_policy_when_closed(self):
        results = run_pilot_preflight(
            make_settings(PRIVATE_PORTAL=True, ALLOW_PUBLIC_REGISTRATION=False),
            profile="private",
        )
        statuses = self.statuses(results)

        self.assertEqual(statuses["private-portal"], "PASS")
        self.assertEqual(statuses["public-registration"], "PASS")

    def test_example_secret_and_wildcard_hosts_always_fail(self):
        results = run_pilot_preflight(
            make_settings(
                SECRET_KEY="replace-with-a-long-random-secret",
                ALLOWED_HOSTS=["*"],
            ),
            profile="public",
        )
        statuses = self.statuses(results)

        self.assertEqual(statuses["secret-key"], "FAIL")
        self.assertEqual(statuses["allowed-hosts"], "FAIL")

    def test_default_brand_is_warning(self):
        results = run_pilot_preflight(
            make_settings(SITE_NAME="VideoShare"),
            profile="public",
        )

        self.assertEqual(self.statuses(results)["site-brand"], "WARN")

    def test_deployment_profile_requires_debug_and_https_cookie_hardening(self):
        results = run_pilot_preflight(
            make_settings(),
            profile="public",
            deployment=True,
        )
        statuses = self.statuses(results)

        self.assertEqual(statuses["debug"], "FAIL")
        self.assertEqual(statuses["ssl-redirect"], "FAIL")
        self.assertEqual(statuses["session-cookie"], "FAIL")
        self.assertEqual(statuses["csrf-cookie"], "FAIL")

    def test_hardened_deployment_passes_security_requirements(self):
        results = run_pilot_preflight(
            make_settings(
                DEBUG=False,
                SECURE_SSL_REDIRECT=True,
                SESSION_COOKIE_SECURE=True,
                CSRF_COOKIE_SECURE=True,
            ),
            profile="public",
            deployment=True,
        )
        statuses = self.statuses(results)

        self.assertEqual(statuses["debug"], "PASS")
        self.assertEqual(statuses["ssl-redirect"], "PASS")
        self.assertEqual(statuses["session-cookie"], "PASS")
        self.assertEqual(statuses["csrf-cookie"], "PASS")
        self.assertNotIn("FAIL", [result.status for result in results])

    def test_stripe_test_mode_is_accepted_without_live_payment_claim(self):
        results = run_pilot_preflight(
            make_settings(
                MONETIZATION_PAYMENT_PROVIDER="stripe",
                STRIPE_SECRET_KEY="sk_test_example",
            ),
            profile="public",
        )

        self.assertEqual(self.statuses(results)["payments"], "PASS")


class PilotCheckCommandTests(SimpleTestCase):
    @override_settings(
        SECRET_KEY="a-unique-secret-key-that-is-long-enough-for-tests",
        ALLOWED_HOSTS=["localhost"],
        SITE_NAME="VideoShare",
        PRIVATE_PORTAL=False,
        ALLOW_PUBLIC_REGISTRATION=True,
        DEBUG=True,
        MONETIZATION_PAYMENT_PROVIDER="sandbox",
        STRIPE_SECRET_KEY="",
    )
    def test_public_command_completes_with_warning_only(self):
        out = StringIO()

        call_command("pilot_check", profile="public", stdout=out)

        output = out.getvalue()
        self.assertIn("Summary:", output)
        self.assertIn("[WARN] site-brand", output)
        self.assertIn("completed with warnings", output)

    @override_settings(
        SECRET_KEY="a-unique-secret-key-that-is-long-enough-for-tests",
        ALLOWED_HOSTS=["localhost"],
        SITE_NAME="Acme Training TV",
        PRIVATE_PORTAL=False,
        ALLOW_PUBLIC_REGISTRATION=True,
        DEBUG=False,
        MONETIZATION_PAYMENT_PROVIDER="sandbox",
        STRIPE_SECRET_KEY="",
    )
    def test_private_command_exits_nonzero_when_access_policy_fails(self):
        out = StringIO()

        with self.assertRaises(CommandError):
            call_command("pilot_check", profile="private", stdout=out)

        output = out.getvalue()
        self.assertIn("[FAIL] private-portal", output)
        self.assertIn("[FAIL] public-registration", output)

    @override_settings(
        SECRET_KEY="a-unique-secret-key-that-is-long-enough-for-tests",
        ALLOWED_HOSTS=["pilot.example.test"],
        SITE_NAME="Acme Training TV",
        PRIVATE_PORTAL=True,
        ALLOW_PUBLIC_REGISTRATION=False,
        DEBUG=False,
        SECURE_SSL_REDIRECT=True,
        SESSION_COOKIE_SECURE=True,
        CSRF_COOKIE_SECURE=True,
        MONETIZATION_PAYMENT_PROVIDER="sandbox",
        STRIPE_SECRET_KEY="",
    )
    def test_private_deployment_command_can_pass_without_warnings(self):
        out = StringIO()

        call_command(
            "pilot_check",
            profile="private",
            deployment=True,
            stdout=out,
        )

        self.assertIn("passed with no warnings", out.getvalue())
