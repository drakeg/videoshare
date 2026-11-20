import csv
import io
from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


def csv_upload(text, name="pilot-users.csv"):
    return SimpleUploadedFile(
        name,
        text.encode("utf-8"),
        content_type="text/csv",
    )


class PilotUserCsvImportTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="operator",
            email="operator@example.com",
            password="password123",
            is_staff=True,
        )
        self.client.force_login(self.staff)
        self.url = reverse("site_admin_pilot_user_csv_import")

    def post_csv(self, text):
        return self.client.post(
            self.url,
            {"csv_file": csv_upload(text)},
        )

    def test_import_endpoint_is_staff_only_and_post_only(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

        anonymous = Client()
        anonymous_response = anonymous.post(
            self.url,
            {"csv_file": csv_upload("username,email\na,a@example.com\n")},
        )
        self.assertEqual(anonymous_response.status_code, 302)
        self.assertIn(reverse("admin:login"), anonymous_response.url)

        viewer = User.objects.create_user(
            username="viewer",
            email="viewer@example.com",
            password="password123",
        )
        nonstaff = Client()
        nonstaff.force_login(viewer)
        nonstaff_response = nonstaff.post(
            self.url,
            {"csv_file": csv_upload("username,email\nb,b@example.com\n")},
        )
        self.assertEqual(nonstaff_response.status_code, 302)
        self.assertIn(reverse("admin:login"), nonstaff_response.url)

    def test_successful_import_creates_only_ordinary_users_and_downloads_setup_links(self):
        response = self.post_csv(
            "username,email,first_name,last_name\n"
            "alpha,alpha@example.com,Alpha,One\n"
            "beta,beta@example.com,Beta,Two\n"
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/csv"))
        self.assertIn(
            'attachment; filename="pilot-user-setup-links.csv"',
            response["Content-Disposition"],
        )

        rows = list(
            csv.DictReader(
                io.StringIO(response.content.decode("utf-8"))
            )
        )
        self.assertEqual([row["username"] for row in rows], ["alpha", "beta"])
        self.assertEqual(
            [row["email"] for row in rows],
            ["alpha@example.com", "beta@example.com"],
        )

        for username in ("alpha", "beta"):
            user = User.objects.get(username=username)
            self.assertTrue(user.is_active)
            self.assertFalse(user.is_staff)
            self.assertFalse(user.is_superuser)
            self.assertTrue(user.has_usable_password())

        alpha = User.objects.get(username="alpha")
        self.assertEqual(alpha.first_name, "Alpha")
        self.assertEqual(alpha.last_name, "One")

        first_setup_path = urlparse(rows[0]["setup_url"]).path
        setup_client = Client()
        setup_response = setup_client.get(first_setup_path)
        self.assertEqual(setup_response.status_code, 302)
        self.assertIn("/set-password/", setup_response.url)

        downloaded = response.content.decode("utf-8").lower()
        self.assertNotIn("temporary_password", downloaded)
        self.assertNotIn("is_staff", downloaded)
        self.assertNotIn("is_superuser", downloaded)

    def test_any_invalid_row_causes_zero_users_to_be_created(self):
        response = self.post_csv(
            "username,email\n"
            "valid-user,valid@example.com\n"
            "invalid-user,not-an-email\n"
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response,
            "Row 3 email: Enter a valid email address.",
            status_code=400,
        )
        self.assertFalse(User.objects.filter(username="valid-user").exists())
        self.assertFalse(User.objects.filter(username="invalid-user").exists())

    def test_duplicate_values_within_csv_are_case_insensitive_and_atomic(self):
        response = self.post_csv(
            "username,email\n"
            "PilotOne,one@example.com\n"
            "pilotone,two@example.com\n"
            "PilotTwo,ONE@example.com\n"
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response,
            "duplicate username within this CSV",
            status_code=400,
        )
        self.assertContains(
            response,
            "duplicate email address within this CSV",
            status_code=400,
        )
        self.assertFalse(User.objects.filter(username__iexact="pilotone").exists())
        self.assertFalse(User.objects.filter(username__iexact="pilottwo").exists())

    def test_existing_username_and_email_collisions_are_case_insensitive_and_atomic(self):
        User.objects.create_user(
            username="ExistingUser",
            email="Existing@Example.com",
            password="password123",
        )

        response = self.post_csv(
            "username,email\n"
            "existinguser,new@example.com\n"
            "new-user,existing@example.com\n"
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response,
            "A user with that username already exists.",
            status_code=400,
        )
        self.assertContains(
            response,
            "A user with that email address already exists.",
            status_code=400,
        )
        self.assertFalse(User.objects.filter(username="new-user").exists())

    def test_missing_or_privilege_headers_are_rejected(self):
        missing = self.post_csv(
            "username,first_name\n"
            "pilot,Test\n"
        )
        self.assertEqual(missing.status_code, 400)
        self.assertContains(
            missing,
            "Missing required CSV header(s): email.",
            status_code=400,
        )

        elevated = self.post_csv(
            "username,email,is_staff\n"
            "pilot,pilot@example.com,true\n"
        )
        self.assertEqual(elevated.status_code, 400)
        self.assertContains(
            elevated,
            "Unexpected CSV header(s): is_staff.",
            status_code=400,
        )
        self.assertFalse(User.objects.filter(username="pilot").exists())

    def test_more_than_200_nonblank_rows_are_rejected_atomically(self):
        lines = ["username,email"]
        lines.extend(
            f"user-{index},user-{index}@example.com"
            for index in range(201)
        )

        response = self.post_csv("\n".join(lines) + "\n")

        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response,
            "at most 200 non-blank users",
            status_code=400,
        )
        self.assertFalse(User.objects.filter(username__startswith="user-").exists())

    def test_oversized_upload_is_rejected_before_import(self):
        oversized = SimpleUploadedFile(
            "too-large.csv",
            b"x" * (100 * 1024 + 1),
            content_type="text/csv",
        )

        response = self.client.post(
            self.url,
            {"csv_file": oversized},
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response,
            "CSV files must be 100 KB or smaller.",
            status_code=400,
        )

    def test_invalid_utf8_is_rejected_without_creating_users(self):
        bad_file = SimpleUploadedFile(
            "bad.csv",
            b"username,email\nuser,user@example.com\xff\n",
            content_type="text/csv",
        )

        response = self.client.post(
            self.url,
            {"csv_file": bad_file},
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response,
            "The CSV must be valid UTF-8 text.",
            status_code=400,
        )
        self.assertFalse(User.objects.filter(username="user").exists())

    def test_extra_row_values_are_rejected_instead_of_silently_ignored(self):
        response = self.post_csv(
            "username,email\n"
            "pilot,pilot@example.com,unexpected\n"
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response,
            "contains more values than the CSV header declares",
            status_code=400,
        )
        self.assertFalse(User.objects.filter(username="pilot").exists())

