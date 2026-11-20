from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .services.pilot_users import pilot_user_directory

User = get_user_model()


class PilotOnboardingStatusTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="operator-status",
            password="password123",
            is_staff=True,
        )
        self.never = User.objects.create_user(
            username="never-signed-in",
            email="never@example.com",
            password="password123",
        )
        self.signed = User.objects.create_user(
            username="signed-in-user",
            email="signed@example.com",
            password="password123",
        )
        self.signed.last_login = timezone.now() - timedelta(days=1)
        self.signed.save(update_fields=["last_login"])
        self.client.force_login(self.staff)

    def test_service_filters_never_and_signed_in_users(self):
        never_page, _, _, never_status = pilot_user_directory(onboarding="never")
        signed_page, _, _, signed_status = pilot_user_directory(onboarding="signed-in")

        self.assertEqual(never_status, "never")
        self.assertIn(self.never, list(never_page.object_list))
        self.assertNotIn(self.signed, list(never_page.object_list))
        self.assertEqual(signed_status, "signed-in")
        self.assertEqual(list(signed_page.object_list), [self.signed])

    def test_invalid_onboarding_filter_falls_back_to_all(self):
        page, _, _, onboarding = pilot_user_directory(onboarding="invalid")

        self.assertEqual(onboarding, "all")
        self.assertEqual(set(page.object_list), {self.never, self.signed})

    def test_directory_displays_never_and_last_sign_in_states(self):
        response = self.client.get(reverse("site_admin_pilot_users"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Never signed in")
        self.assertContains(response, "Last sign-in")
        self.assertContains(response, "@signed-in-user")

    def test_filters_compose_with_search_and_account_status(self):
        User.objects.create_user(
            username="never-suspended",
            email="never-suspended@example.com",
            password="password123",
            is_active=False,
        )

        response = self.client.get(
            reverse("site_admin_pilot_users"),
            {"q": "never", "status": "active", "onboarding": "never"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "@never-signed-in")
        self.assertNotContains(response, "@never-suspended")
        self.assertNotContains(response, "@signed-in-user")
        self.assertEqual(response.context["pilot_user_onboarding"], "never")

    def test_pager_preserves_onboarding_filter(self):
        User.objects.bulk_create(
            [
                User(
                    username=f"never-cohort-{index:03d}",
                    email=f"never-{index:03d}@example.com",
                    is_active=True,
                )
                for index in range(51)
            ]
        )

        response = self.client.get(
            reverse("site_admin_pilot_users"),
            {"q": "never", "status": "active", "onboarding": "never"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Page 1 of 2")
        self.assertContains(
            response,
            "q=never&status=active&onboarding=never&page=2",
        )
