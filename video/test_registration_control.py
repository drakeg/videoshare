from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse


class PublicRegistrationControlTests(TestCase):
    def test_public_registration_is_enabled_by_default(self):
        response = self.client.get(reverse("register"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create an account")

    @override_settings(ALLOW_PUBLIC_REGISTRATION=False)
    def test_disabled_registration_get_is_forbidden(self):
        response = self.client.get(reverse("register"))

        self.assertEqual(response.status_code, 403)
        self.assertContains(
            response,
            "Public registration is disabled.",
            status_code=403,
        )

    @override_settings(ALLOW_PUBLIC_REGISTRATION=False)
    def test_disabled_registration_post_creates_no_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "blocked-user",
                "password1": "a-secure-password-12345",
                "password2": "a-secure-password-12345",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(User.objects.filter(username="blocked-user").exists())

    @override_settings(ALLOW_PUBLIC_REGISTRATION=False)
    def test_signup_links_are_hidden_when_registration_is_disabled(self):
        home = self.client.get(reverse("video_list"))
        login = self.client.get(reverse("login"))

        self.assertNotContains(home, reverse("register"))
        self.assertNotContains(login, reverse("register"))
        self.assertContains(login, reverse("password_reset"))

    @override_settings(ALLOW_PUBLIC_REGISTRATION=False)
    def test_existing_user_can_still_log_in(self):
        user = User.objects.create_user(
            username="existing-user",
            password="password123",
        )

        response = self.client.post(
            reverse("login"),
            {
                "username": user.username,
                "password": "password123",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)
