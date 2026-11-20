from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PilotUserResetLinkTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="operator",
            email="operator@example.com",
            password="password123",
            is_staff=True,
        )
        self.user = User.objects.create_user(
            username="pilot-user",
            email="pilot@example.com",
            password="existing-password-12345",
        )
        self.client.force_login(self.staff)

    def test_active_ordinary_user_has_generate_reset_link_action(self):
        response = self.client.get(reverse("site_admin_pilot_users"))

        self.assertContains(
            response,
            reverse("site_admin_pilot_user_reset_link", kwargs={"pk": self.user.pk}),
        )
        self.assertContains(response, "Generate reset link")

    def test_reset_link_action_is_post_only(self):
        response = self.client.get(
            reverse("site_admin_pilot_user_reset_link", kwargs={"pk": self.user.pk})
        )

        self.assertEqual(response.status_code, 405)

    def test_anonymous_and_nonstaff_users_cannot_generate_reset_link(self):
        target = reverse(
            "site_admin_pilot_user_reset_link",
            kwargs={"pk": self.user.pk},
        )

        anonymous = Client()
        anonymous_response = anonymous.post(target)
        self.assertEqual(anonymous_response.status_code, 302)
        self.assertIn(reverse("admin:login"), anonymous_response.url)

        nonstaff = Client()
        nonstaff.force_login(self.user)
        nonstaff_response = nonstaff.post(target)
        self.assertEqual(nonstaff_response.status_code, 302)
        self.assertIn(reverse("admin:login"), nonstaff_response.url)

    def test_action_rejects_inactive_staff_and_superuser_targets(self):
        inactive = User.objects.create_user(
            username="inactive",
            password="password123",
            is_active=False,
        )
        staff_target = User.objects.create_user(
            username="staff-target",
            password="password123",
            is_staff=True,
        )
        superuser = User.objects.create_superuser(
            username="super-target",
            email="super@example.com",
            password="password123",
        )

        for target_user in (inactive, staff_target, superuser):
            with self.subTest(username=target_user.username):
                response = self.client.post(
                    reverse(
                        "site_admin_pilot_user_reset_link",
                        kwargs={"pk": target_user.pk},
                    )
                )
                self.assertEqual(response.status_code, 404)

    def test_generating_link_does_not_mutate_existing_account(self):
        original_password = self.user.password
        original_email = self.user.email
        original_active = self.user.is_active
        original_staff = self.user.is_staff
        original_superuser = self.user.is_superuser

        response = self.client.post(
            reverse(
                "site_admin_pilot_user_reset_link",
                kwargs={"pk": self.user.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.password, original_password)
        self.assertEqual(self.user.email, original_email)
        self.assertEqual(self.user.is_active, original_active)
        self.assertEqual(self.user.is_staff, original_staff)
        self.assertEqual(self.user.is_superuser, original_superuser)
        self.assertTrue(self.user.check_password("existing-password-12345"))
        self.assertContains(response, "Reset link generated for @pilot-user")
        self.assertContains(
            response,
            "does not change the user&#x27;s current password",
            html=False,
        )

    def test_generated_link_can_reset_existing_password(self):
        response = self.client.post(
            reverse(
                "site_admin_pilot_user_reset_link",
                kwargs={"pk": self.user.pk},
            )
        )
        setup_path = urlparse(response.context["setup_url"]).path

        user_client = Client()
        token_response = user_client.get(setup_path)
        self.assertEqual(token_response.status_code, 302)
        self.assertIn("/set-password/", token_response.url)

        form_response = user_client.get(token_response.url)
        self.assertEqual(form_response.status_code, 200)
        self.assertContains(form_response, "Choose a password")

        completion = user_client.post(
            token_response.url,
            {
                "new_password1": "A-new-pilot-password-67890",
                "new_password2": "A-new-pilot-password-67890",
            },
            follow=True,
        )
        self.assertEqual(completion.status_code, 200)
        self.assertContains(completion, "Your password is set")

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("A-new-pilot-password-67890"))
        self.assertFalse(self.user.check_password("existing-password-12345"))

    def test_inactive_users_show_reactivate_guidance_instead_of_action(self):
        inactive = User.objects.create_user(
            username="inactive-viewer",
            password="password123",
            is_active=False,
        )

        response = self.client.get(reverse("site_admin_pilot_users"))

        self.assertContains(response, "Reactivate first")
        self.assertNotContains(
            response,
            reverse(
                "site_admin_pilot_user_reset_link",
                kwargs={"pk": inactive.pk},
            ),
        )
