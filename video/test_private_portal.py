from urllib.parse import parse_qs, urlparse

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from .middleware import PrivatePortalMiddleware


class PrivatePortalTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_private_portal_is_disabled_by_default(self):
        response = self.client.get(reverse("video_list"))

        self.assertEqual(response.status_code, 200)

    @override_settings(PRIVATE_PORTAL=True)
    def test_anonymous_application_request_redirects_to_login(self):
        response = self.client.get(reverse("video_list"))

        self.assertEqual(response.status_code, 302)
        parsed = urlparse(response.url)
        self.assertEqual(parsed.path, reverse("login"))
        self.assertEqual(parse_qs(parsed.query)["next"], [reverse("video_list")])

    @override_settings(PRIVATE_PORTAL=True)
    def test_redirect_preserves_requested_query_string(self):
        target = reverse("search") + "?query=solar&sort=views"
        response = self.client.get(target)

        parsed = urlparse(response.url)
        self.assertEqual(parsed.path, reverse("login"))
        self.assertEqual(parse_qs(parsed.query)["next"], [target])

    @override_settings(PRIVATE_PORTAL=True)
    def test_authenticated_user_keeps_normal_access(self):
        user = User.objects.create_user(username="viewer", password="password123")
        self.client.force_login(user)

        response = self.client.get(reverse("video_list"))

        self.assertEqual(response.status_code, 200)

    @override_settings(PRIVATE_PORTAL=True)
    def test_login_registration_and_admin_auth_remain_reachable(self):
        self.assertEqual(self.client.get(reverse("login")).status_code, 200)
        self.assertEqual(self.client.get(reverse("register")).status_code, 200)

        admin_response = self.client.get(reverse("admin:index"))
        self.assertEqual(admin_response.status_code, 302)
        self.assertTrue(admin_response.url.startswith(reverse("admin:login")))

    @override_settings(PRIVATE_PORTAL=True)
    def test_password_reset_routes_are_public_exceptions(self):
        middleware = PrivatePortalMiddleware(lambda request: None)
        request = self.factory.get(reverse("password_reset"))
        request.user = AnonymousUser()

        self.assertTrue(middleware._is_public_path(request))

    @override_settings(PRIVATE_PORTAL=True)
    def test_static_assets_are_not_forced_through_login(self):
        response = self.client.get("/static/style.css")

        self.assertNotEqual(response.status_code, 302)
        self.assertNotEqual(getattr(response, "url", ""), reverse("login"))

    @override_settings(PRIVATE_PORTAL=True)
    def test_local_media_path_is_gated_while_signed_out(self):
        response = self.client.get("/media/example.jpg")

        self.assertEqual(response.status_code, 302)
        parsed = urlparse(response.url)
        self.assertEqual(parsed.path, reverse("login"))
        self.assertEqual(parse_qs(parsed.query)["next"], ["/media/example.jpg"])
