import csv
from datetime import timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


class PilotUserDirectoryExportTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="export-operator",
            password="password123",
            is_staff=True,
        )
        self.client.force_login(self.staff)
        self.url = reverse("site_admin_pilot_user_export")

    def rows(self, response):
        return list(csv.DictReader(StringIO(response.content.decode("utf-8"))))

    def test_export_is_staff_only_and_excludes_privileged_accounts(self):
        ordinary = User.objects.create_user(
            username="ordinary-export",
            email="ordinary@example.com",
            password="password123",
        )
        User.objects.create_user(
            username="other-staff",
            password="password123",
            is_staff=True,
        )
        User.objects.create_superuser(
            username="other-super",
            email="super@example.com",
            password="password123",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Disposition"],
            'attachment; filename="pilot-users.csv"',
        )
        usernames = {row["username"] for row in self.rows(response)}
        self.assertIn(ordinary.username, usernames)
        self.assertNotIn("export-operator", usernames)
        self.assertNotIn("other-staff", usernames)
        self.assertNotIn("other-super", usernames)

        anonymous = Client()
        anonymous_response = anonymous.get(self.url)
        self.assertEqual(anonymous_response.status_code, 302)
        self.assertIn(reverse("admin:login"), anonymous_response.url)

        nonstaff = Client()
        nonstaff.force_login(ordinary)
        nonstaff_response = nonstaff.get(self.url)
        self.assertEqual(nonstaff_response.status_code, 302)
        self.assertIn(reverse("admin:login"), nonstaff_response.url)

    def test_export_reuses_directory_filters(self):
        signed = User.objects.create_user(
            username="alpha-signed",
            email="alpha-signed@example.com",
            password="password123",
            is_active=True,
        )
        signed.last_login = timezone.now() - timedelta(days=2)
        signed.save(update_fields=["last_login"])
        User.objects.create_user(
            username="alpha-never",
            email="alpha-never@example.com",
            password="password123",
            is_active=True,
        )
        User.objects.create_user(
            username="alpha-suspended",
            email="alpha-suspended@example.com",
            password="password123",
            is_active=False,
        )
        User.objects.create_user(
            username="beta-signed",
            email="beta@example.com",
            password="password123",
        )

        response = self.client.get(
            self.url,
            {
                "q": "alpha",
                "status": "active",
                "onboarding": "signed-in",
            },
        )

        rows = self.rows(response)
        self.assertEqual([row["username"] for row in rows], ["alpha-signed"])
        self.assertEqual(rows[0]["account_status"], "active")
        self.assertEqual(rows[0]["sign_in_status"], "signed-in")
        self.assertEqual(rows[0]["last_login"], signed.last_login.isoformat())

    def test_export_includes_all_matches_independent_of_ui_page(self):
        User.objects.bulk_create(
            [
                User(
                    username=f"cohort-export-{index:03d}",
                    email=f"cohort-{index:03d}@example.com",
                    is_active=True,
                )
                for index in range(61)
            ]
        )

        response = self.client.get(
            self.url,
            {
                "q": "cohort-export",
                "status": "active",
                "onboarding": "never",
                "page": "2",
            },
        )

        rows = self.rows(response)
        self.assertEqual(len(rows), 61)
        self.assertEqual(
            {row["username"] for row in rows},
            {f"cohort-export-{index:03d}" for index in range(61)},
        )

    def test_export_headers_exclude_authentication_secrets(self):
        user = User.objects.create_user(
            username="secret-check",
            email="secret@example.com",
            password="Sensitive-password-12345",
        )

        response = self.client.get(self.url)
        content = response.content.decode("utf-8")
        reader = csv.reader(StringIO(content))
        headers = next(reader)

        self.assertEqual(
            headers,
            [
                "username",
                "email",
                "first_name",
                "last_name",
                "account_status",
                "sign_in_status",
                "last_login",
                "date_joined",
            ],
        )
        for forbidden in ("password", "setup_url", "reset", "token"):
            self.assertNotIn(forbidden, ",".join(headers).lower())
        self.assertNotIn(user.password, content)
        self.assertNotIn("Sensitive-password-12345", content)

    def test_user_controlled_formula_like_text_is_neutralized(self):
        User.objects.create(
            username="formula-user",
            email="formula@example.com",
            first_name="=HYPERLINK(\"https://example.com\")",
            last_name="+SUM(1,1)",
        )

        response = self.client.get(self.url, {"q": "formula-user"})
        row = self.rows(response)[0]

        self.assertTrue(row["first_name"].startswith("'="))
        self.assertTrue(row["last_name"].startswith("'+"))

    def test_directory_export_link_preserves_current_filters(self):
        User.objects.create_user(
            username="filter-link",
            email="filter-link@example.com",
            password="password123",
        )

        response = self.client.get(
            reverse("site_admin_pilot_users"),
            {
                "q": "filter",
                "status": "active",
                "onboarding": "never",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("site_admin_pilot_user_export"))
        self.assertContains(
            response,
            "q=filter&status=active&onboarding=never",
        )
