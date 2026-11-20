from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .moderation_models import ModerationAuditEvent

User = get_user_model()


class PilotUserAccessStateTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="pilot-operator",
            password="password123",
            is_staff=True,
        )
        self.user = User.objects.create_user(
            username="pilot-viewer",
            email="pilot@example.com",
            password="password123",
            is_active=True,
        )
        self.client.force_login(self.staff)
        self.url = reverse(
            "site_admin_pilot_user_access_state",
            kwargs={"pk": self.user.pk},
        )

    def post_state(self, *, action, reason="Pilot access change", **return_state):
        data = {
            "action": action,
            "reason": reason,
            "q": return_state.get("q", ""),
            "status": return_state.get("status", "all"),
            "onboarding": return_state.get("onboarding", "all"),
            "page": return_state.get("page", "1"),
        }
        return self.client.post(self.url, data)

    def test_staff_can_suspend_ordinary_user_with_audit_event(self):
        response = self.post_state(
            action="suspend",
            reason="Pilot access paused",
            q="pilot",
            status="active",
            onboarding="never",
            page="2",
        )

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

        audit = ModerationAuditEvent.objects.get(
            action="user_suspend",
            target_type="user",
            target_id=self.user.pk,
        )
        self.assertEqual(audit.actor, self.staff)
        self.assertEqual(audit.reason, "Pilot access paused")

        parsed = urlparse(response.url)
        self.assertEqual(parsed.path, reverse("site_admin_pilot_users"))
        self.assertEqual(
            parse_qs(parsed.query),
            {
                "q": ["pilot"],
                "status": ["active"],
                "onboarding": ["never"],
                "page": ["2"],
            },
        )

    def test_staff_can_reactivate_suspended_ordinary_user(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.post_state(
            action="reactivate",
            reason="Pilot access restored",
        )

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        audit = ModerationAuditEvent.objects.get(
            action="user_reactivate",
            target_type="user",
            target_id=self.user.pk,
        )
        self.assertEqual(audit.reason, "Pilot access restored")

    def test_reason_is_required_and_failure_does_not_change_state(self):
        response = self.post_state(action="suspend", reason="   ")

        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response,
            "A moderation reason is required.",
            status_code=400,
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertFalse(
            ModerationAuditEvent.objects.filter(
                target_type="user",
                target_id=self.user.pk,
            ).exists()
        )

    def test_invalid_action_is_rejected(self):
        response = self.post_state(action="delete", reason="Not allowed")

        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_staff_superuser_and_missing_targets_are_rejected(self):
        staff_target = User.objects.create_user(
            username="staff-target",
            password="password123",
            is_staff=True,
        )
        super_target = User.objects.create_superuser(
            username="super-target",
            email="super@example.com",
            password="password123",
        )

        for pk in (staff_target.pk, super_target.pk, 999999):
            with self.subTest(pk=pk):
                response = self.client.post(
                    reverse(
                        "site_admin_pilot_user_access_state",
                        kwargs={"pk": pk},
                    ),
                    {"action": "suspend", "reason": "No"},
                )
                self.assertEqual(response.status_code, 404)

    def test_nonstaff_callers_remain_blocked(self):
        target = self.url

        anonymous = Client()
        anonymous_response = anonymous.post(
            target,
            {"action": "suspend", "reason": "No access"},
        )
        self.assertEqual(anonymous_response.status_code, 302)
        self.assertIn(reverse("admin:login"), anonymous_response.url)

        nonstaff = Client()
        nonstaff.force_login(self.user)
        nonstaff_response = nonstaff.post(
            target,
            {"action": "suspend", "reason": "No access"},
        )
        self.assertEqual(nonstaff_response.status_code, 302)
        self.assertIn(reverse("admin:login"), nonstaff_response.url)

    def test_invalid_return_state_is_normalized_safely(self):
        response = self.post_state(
            action="suspend",
            reason="Normalize return state",
            q=" x " * 80,
            status="invalid",
            onboarding="invalid",
            page="-9",
        )

        self.assertEqual(response.status_code, 302)
        parsed = urlparse(response.url)
        params = parse_qs(parsed.query)
        self.assertEqual(params["status"], ["all"])
        self.assertEqual(params["onboarding"], ["all"])
        self.assertEqual(params["page"], ["1"])
        self.assertLessEqual(len(params["q"][0]), 100)

    def test_directory_switches_to_reactivate_and_hides_reset_actions_when_suspended(self):
        self.post_state(action="suspend", reason="Temporary suspension")

        response = self.client.get(reverse("site_admin_pilot_users"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reactivate")
        self.assertContains(response, "Reactivate first to restore setup/reset actions")
        self.assertNotContains(
            response,
            reverse(
                "site_admin_pilot_user_reset_link",
                kwargs={"pk": self.user.pk},
            ),
        )
