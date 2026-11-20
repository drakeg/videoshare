from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .services.pilot_users import send_pilot_user_setup_email

User = get_user_model()


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="pilot-ops@example.com",
    SITE_NAME="Acme Training TV",
)
class PilotUserSetupEmailTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="operator",
            email="operator@example.com",
            password="password123",
            is_staff=True,
        )
        self.client.force_login(self.staff)

    def test_delivery_is_disabled_by_default(self):
        user = User.objects.create_user(
            username="pilot",
            email="pilot@example.com",
            password="password123",
        )

        status = send_pilot_user_setup_email(
            user=user,
            setup_url="https://pilot.example.test/accounts/reset/example/",
        )

        self.assertEqual(status, "disabled")
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(PILOT_USER_SETUP_EMAIL_ENABLED=True)
    def test_service_sends_branded_setup_email(self):
        user = User.objects.create_user(
            username="pilot",
            email="pilot@example.com",
            first_name="Pat",
            password="password123",
        )
        setup_url = "https://pilot.example.test/accounts/reset/example/"

        status = send_pilot_user_setup_email(
            user=user,
            setup_url=setup_url,
            purpose="setup",
        )

        self.assertEqual(status, "sent")
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.subject, "Set up your Acme Training TV account")
        self.assertEqual(message.from_email, "pilot-ops@example.com")
        self.assertEqual(message.to, ["pilot@example.com"])
        self.assertIn("Hello Pat", message.body)
        self.assertIn(setup_url, message.body)

    @override_settings(PILOT_USER_SETUP_EMAIL_ENABLED=True)
    def test_missing_recipient_email_does_not_send(self):
        user = User.objects.create_user(
            username="no-email",
            email="",
            password="password123",
        )

        status = send_pilot_user_setup_email(
            user=user,
            setup_url="https://pilot.example.test/reset/",
            purpose="reset",
        )

        self.assertEqual(status, "missing_email")
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(PILOT_USER_SETUP_EMAIL_ENABLED=True)
    @patch("video.services.pilot_users.send_mail", side_effect=RuntimeError("mail unavailable"))
    def test_backend_failure_is_safe_and_does_not_raise(self, mocked_send_mail):
        user = User.objects.create_user(
            username="mail-failure",
            email="mail-failure@example.com",
            password="existing-password-12345",
        )
        original_password = user.password

        status = send_pilot_user_setup_email(
            user=user,
            setup_url="https://pilot.example.test/reset/",
            purpose="reset",
        )

        self.assertEqual(status, "failed")
        mocked_send_mail.assert_called_once()
        user.refresh_from_db()
        self.assertEqual(user.password, original_password)
        self.assertTrue(user.check_password("existing-password-12345"))

    def test_disabled_page_does_not_offer_email_actions(self):
        user = User.objects.create_user(
            username="existing",
            email="existing@example.com",
            password="password123",
        )

        response = self.client.get(reverse("site_admin_pilot_users"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Email the password-setup link")
        self.assertNotContains(response, "Email reset link")
        self.assertContains(response, "Generate reset link")
        self.assertContains(response, f"@{user.username}")

    @override_settings(PILOT_USER_SETUP_EMAIL_ENABLED=True)
    def test_staff_can_email_new_user_setup_link_and_keep_manual_url(self):
        response = self.client.post(
            reverse("site_admin_pilot_users"),
            {
                "username": "emailed-new-user",
                "email": "new-user@example.com",
                "first_name": "New",
                "last_name": "User",
                "send_setup_email": "on",
            },
        )

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username="emailed-new-user")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(response.context["email_delivery_status"], "sent")
        self.assertContains(response, "Email sent.")
        self.assertContains(response, "Password setup/reset URL")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(response.context["setup_url"], mail.outbox[0].body)

    @override_settings(PILOT_USER_SETUP_EMAIL_ENABLED=True)
    def test_staff_can_email_existing_user_reset_link(self):
        user = User.objects.create_user(
            username="existing-pilot",
            email="existing-pilot@example.com",
            password="existing-password-12345",
        )
        original_password = user.password

        list_response = self.client.get(reverse("site_admin_pilot_users"))
        self.assertContains(list_response, "Email reset link")

        response = self.client.post(
            reverse(
                "site_admin_pilot_user_reset_link",
                kwargs={"pk": user.pk},
            ),
            {"delivery": "email"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["email_delivery_status"], "sent")
        self.assertContains(response, "Email sent.")
        self.assertContains(response, "Password setup/reset URL")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            "Reset your Acme Training TV password",
        )
        self.assertIn(response.context["setup_url"], mail.outbox[0].body)

        user.refresh_from_db()
        self.assertEqual(user.password, original_password)
        self.assertTrue(user.check_password("existing-password-12345"))

    @override_settings(PILOT_USER_SETUP_EMAIL_ENABLED=True)
    @patch("video.services.pilot_users.send_mail", side_effect=RuntimeError("mail unavailable"))
    def test_email_failure_preserves_manual_link_after_new_user_creation(self, mocked_send_mail):
        response = self.client.post(
            reverse("site_admin_pilot_users"),
            {
                "username": "fallback-user",
                "email": "fallback@example.com",
                "send_setup_email": "on",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="fallback-user").exists())
        self.assertEqual(response.context["email_delivery_status"], "failed")
        self.assertContains(response, "Email could not be sent.")
        self.assertContains(response, response.context["setup_url"])
        mocked_send_mail.assert_called_once()

    @override_settings(PILOT_USER_SETUP_EMAIL_ENABLED=True)
    def test_direct_email_request_without_recipient_preserves_manual_link(self):
        user = User.objects.create_user(
            username="no-email-existing",
            email="",
            password="password123",
        )

        response = self.client.post(
            reverse(
                "site_admin_pilot_user_reset_link",
                kwargs={"pk": user.pk},
            ),
            {"delivery": "email"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["email_delivery_status"], "missing_email")
        self.assertContains(response, "No recipient email is available.")
        self.assertContains(response, "Password setup/reset URL")
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(PILOT_USER_SETUP_EMAIL_ENABLED=True)
    def test_bulk_csv_import_does_not_send_email_automatically(self):
        csv_file = SimpleUploadedFile(
            "pilot-users.csv",
            b"username,email\nbulk-one,bulk-one@example.com\n",
            content_type="text/csv",
        )

        response = self.client.post(
            reverse("site_admin_pilot_user_csv_import"),
            {"csv_file": csv_file},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="bulk-one").exists())
        self.assertEqual(len(mail.outbox), 0)
