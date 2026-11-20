from unittest.mock import patch
from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse

User = get_user_model()


class PilotUserProvisioningTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="operator",
            email="operator@example.com",
            password="password123",
            is_staff=True,
        )
        self.client.force_login(self.staff)

    def test_staff_only_page_rejects_anonymous_and_nonstaff_users(self):
        anonymous = Client()
        anonymous_response = anonymous.get(reverse("site_admin_pilot_users"))
        self.assertEqual(anonymous_response.status_code, 302)
        self.assertIn(reverse("admin:login"), anonymous_response.url)

        viewer = User.objects.create_user(
            username="viewer",
            email="viewer@example.com",
            password="password123",
        )
        nonstaff = Client()
        nonstaff.force_login(viewer)
        nonstaff_response = nonstaff.get(reverse("site_admin_pilot_users"))
        self.assertEqual(nonstaff_response.status_code, 302)
        self.assertIn(reverse("admin:login"), nonstaff_response.url)

    def test_site_admin_dashboard_links_to_pilot_users(self):
        response = self.client.get(reverse("site_admin_dashboard"))

        self.assertContains(response, reverse("site_admin_pilot_users"))
        self.assertContains(response, "Pilot users")

    @patch("video.services.pilot_users.secrets.token_urlsafe", return_value="internal-random-password")
    def test_staff_can_provision_ordinary_user_and_get_setup_link(self, mocked_secret):
        response = self.client.post(
            reverse("site_admin_pilot_users"),
            {
                "username": "pilot-viewer",
                "email": "pilot@example.com",
                "first_name": "Pilot",
                "last_name": "Viewer",
            },
        )

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username="pilot-viewer")
        self.assertEqual(user.email, "pilot@example.com")
        self.assertEqual(user.first_name, "Pilot")
        self.assertEqual(user.last_name, "Viewer")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password("internal-random-password"))
        mocked_secret.assert_called_once_with(32)

        self.assertNotContains(response, "internal-random-password")
        setup_url = response.context["setup_url"]
        self.assertTrue(setup_url.startswith("http://testserver/"))
        self.assertIn("/accounts/reset/", setup_url)

    def test_duplicate_username_or_email_does_not_create_user(self):
        User.objects.create_user(
            username="Existing",
            email="Existing@Example.com",
            password="password123",
        )

        username_response = self.client.post(
            reverse("site_admin_pilot_users"),
            {
                "username": "existing",
                "email": "new@example.com",
            },
        )
        self.assertContains(
            username_response,
            "A user with that username already exists.",
        )

        email_response = self.client.post(
            reverse("site_admin_pilot_users"),
            {
                "username": "new-user",
                "email": "existing@example.com",
            },
        )
        self.assertContains(
            email_response,
            "A user with that email address already exists.",
        )

        self.assertEqual(User.objects.filter(is_staff=False).count(), 1)
        self.assertFalse(User.objects.filter(username="new-user").exists())

    def test_generated_setup_link_can_set_password_and_login(self):
        response = self.client.post(
            reverse("site_admin_pilot_users"),
            {
                "username": "setup-user",
                "email": "setup@example.com",
            },
        )
        setup_url = response.context["setup_url"]
        setup_path = urlparse(setup_url).path

        user_client = Client()
        confirm_response = user_client.get(setup_path)
        self.assertEqual(confirm_response.status_code, 302)
        self.assertIn("/set-password/", confirm_response.url)

        form_response = user_client.get(confirm_response.url)
        self.assertEqual(form_response.status_code, 200)
        self.assertContains(form_response, "Choose a password")

        complete_response = user_client.post(
            confirm_response.url,
            {
                "new_password1": "A-strong-new-password-12345",
                "new_password2": "A-strong-new-password-12345",
            },
            follow=True,
        )
        self.assertEqual(complete_response.status_code, 200)
        self.assertContains(complete_response, "Your password is set")

        login_response = user_client.post(
            reverse("login"),
            {
                "username": "setup-user",
                "password": "A-strong-new-password-12345",
            },
        )
        self.assertEqual(login_response.status_code, 302)
        self.assertIn("_auth_user_id", user_client.session)


class PasswordResetTemplateTests(TestCase):
    def test_password_reset_form_and_done_pages_render(self):
        form_response = self.client.get(reverse("password_reset"))
        done_response = self.client.get(reverse("password_reset_done"))

        self.assertEqual(form_response.status_code, 200)
        self.assertContains(form_response, "Reset your password")
        self.assertEqual(done_response.status_code, 200)
        self.assertContains(done_response, "Check your email")

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="noreply@example.com",
    )
    def test_existing_user_can_request_branded_password_reset_email(self):
        User.objects.create_user(
            username="reset-user",
            email="reset@example.com",
            password="password123",
        )

        response = self.client.post(
            reverse("password_reset"),
            {"email": "reset@example.com"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Check your email")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Reset your VideoShare password", mail.outbox[0].subject)
        self.assertIn("/accounts/reset/", mail.outbox[0].body)
