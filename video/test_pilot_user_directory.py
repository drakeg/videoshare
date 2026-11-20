from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .services.pilot_users import (
    PILOT_USER_PAGE_SIZE,
    PILOT_USER_SEARCH_MAX_LENGTH,
    pilot_user_directory,
)

User = get_user_model()


class PilotUserDirectoryServiceTests(TestCase):
    def test_search_is_trimmed_bounded_and_matches_all_supported_name_fields(self):
        target = User.objects.create(
            username="target-user",
            email="target@example.com",
            first_name="TargetFirst",
            last_name="TargetLast",
            is_active=True,
        )
        User.objects.create(username="other", email="other@example.com")

        for query in (
            " target-user ",
            "TARGET@EXAMPLE.COM",
            "targetfirst",
            "TARGETLAST",
        ):
            with self.subTest(query=query):
                page, normalized_query, status = pilot_user_directory(query=query)
                self.assertEqual(status, "all")
                self.assertEqual(list(page.object_list), [target])
                self.assertEqual(normalized_query, query.strip()[:PILOT_USER_SEARCH_MAX_LENGTH])

        long_prefix = "x" * PILOT_USER_SEARCH_MAX_LENGTH
        bounded_user = User.objects.create(
            username=f"{long_prefix}tail",
            email="bounded@example.com",
        )
        page, normalized_query, _ = pilot_user_directory(
            query=f"  {long_prefix}ignored-suffix  "
        )
        self.assertEqual(len(normalized_query), PILOT_USER_SEARCH_MAX_LENGTH)
        self.assertIn(bounded_user, list(page.object_list))

    def test_status_filter_and_invalid_fallback(self):
        active = User.objects.create(username="active-user", is_active=True)
        suspended = User.objects.create(username="suspended-user", is_active=False)

        active_page, _, active_status = pilot_user_directory(status="active")
        suspended_page, _, suspended_status = pilot_user_directory(status="suspended")
        fallback_page, _, fallback_status = pilot_user_directory(status="invalid")

        self.assertEqual(active_status, "active")
        self.assertEqual(list(active_page.object_list), [active])
        self.assertEqual(suspended_status, "suspended")
        self.assertEqual(list(suspended_page.object_list), [suspended])
        self.assertEqual(fallback_status, "all")
        self.assertEqual(set(fallback_page.object_list), {active, suspended})

    def test_directory_excludes_staff_and_superusers(self):
        ordinary = User.objects.create(username="ordinary")
        User.objects.create(username="staff", is_staff=True)
        User.objects.create(username="super", is_staff=True, is_superuser=True)

        page, _, _ = pilot_user_directory()

        self.assertEqual(list(page.object_list), [ordinary])

    def test_directory_paginates_at_fifty_users(self):
        User.objects.bulk_create(
            [User(username=f"pilot-{index:03d}") for index in range(PILOT_USER_PAGE_SIZE + 11)]
        )

        first_page, _, _ = pilot_user_directory(page=1)
        second_page, _, _ = pilot_user_directory(page=2)

        self.assertEqual(first_page.paginator.per_page, PILOT_USER_PAGE_SIZE)
        self.assertEqual(first_page.paginator.count, PILOT_USER_PAGE_SIZE + 11)
        self.assertEqual(len(first_page.object_list), PILOT_USER_PAGE_SIZE)
        self.assertEqual(len(second_page.object_list), 11)


class PilotUserDirectoryViewTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="operator",
            email="operator@example.com",
            password="password123",
            is_staff=True,
        )
        self.client.force_login(self.staff)

    def test_nonstaff_access_remains_blocked(self):
        viewer = User.objects.create_user(
            username="viewer",
            password="password123",
        )
        client = Client()
        client.force_login(viewer)

        response = client.get(reverse("site_admin_pilot_users"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin:login"), response.url)

    def test_page_filters_by_query_and_status_and_preserves_row_actions(self):
        active = User.objects.create_user(
            username="alpha-active",
            email="alpha@example.com",
            password="password123",
            is_active=True,
        )
        User.objects.create_user(
            username="alpha-suspended",
            email="suspended@example.com",
            password="password123",
            is_active=False,
        )
        User.objects.create_user(
            username="other-active",
            email="other@example.com",
            password="password123",
            is_active=True,
        )

        response = self.client.get(
            reverse("site_admin_pilot_users"),
            {"q": "alpha", "status": "active"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "@alpha-active")
        self.assertNotContains(response, "@alpha-suspended")
        self.assertNotContains(response, "@other-active")
        self.assertContains(
            response,
            reverse("site_admin_pilot_user_reset_link", kwargs={"pk": active.pk}),
        )
        self.assertEqual(response.context["pilot_user_query"], "alpha")
        self.assertEqual(response.context["pilot_user_status"], "active")

    def test_invalid_status_falls_back_to_all(self):
        User.objects.create_user(username="active-one", password="password123")
        User.objects.create_user(
            username="suspended-one",
            password="password123",
            is_active=False,
        )

        response = self.client.get(
            reverse("site_admin_pilot_users"),
            {"status": "not-a-real-filter"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["pilot_user_status"], "all")
        self.assertContains(response, "@active-one")
        self.assertContains(response, "@suspended-one")

    def test_pagination_links_preserve_query_and_status(self):
        User.objects.bulk_create(
            [
                User(
                    username=f"cohort-{index:03d}",
                    email=f"cohort-{index:03d}@example.com",
                    is_active=True,
                )
                for index in range(PILOT_USER_PAGE_SIZE + 1)
            ]
        )

        response = self.client.get(
            reverse("site_admin_pilot_users"),
            {"q": "cohort", "status": "active", "page": 1},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Page 1 of 2")
        self.assertContains(response, "q=cohort&amp;status=active&amp;page=2")
        self.assertContains(response, ">Next</a>", html=False)

    def test_search_form_resets_stale_page_and_caps_input(self):
        overlong_query = "x" * (PILOT_USER_SEARCH_MAX_LENGTH + 25)

        response = self.client.get(
            reverse("site_admin_pilot_users"),
            {"q": overlong_query, "status": "all", "page": 99},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["pilot_user_query"],
            "x" * PILOT_USER_SEARCH_MAX_LENGTH,
        )
        self.assertContains(response, 'maxlength="100"')
        self.assertNotContains(response, 'name="page"')
