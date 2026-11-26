from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse


class PrivatePortalLoginExperienceTests(TestCase):
    @override_settings(PRIVATE_PORTAL=True, ALLOW_PUBLIC_REGISTRATION=False,
                       SITE_NAME="Acme Training", SITE_TAGLINE="Learn with your team.")
    def test_signed_out_private_portal_login_is_branded_and_hides_content_navigation(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, "Sign in to access Acme Training.")
        self.assertContains(response, "Learn with your team.")
        self.assertNotContains(response, 'aria-label="Primary navigation"')
        self.assertNotContains(response, 'id="site-search"')
        self.assertNotContains(response, 'id="mobile-site-search"')
        self.assertContains(response, reverse("password_reset"))
        self.assertNotContains(response, 'href="' + reverse("register") + '"')

    @override_settings(PRIVATE_PORTAL=False)
    def test_public_login_retains_discovery_navigation(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, 'aria-label="Primary navigation"')
        self.assertContains(response, 'id="site-search"')

    @override_settings(PRIVATE_PORTAL=True)
    def test_authenticated_private_portal_retains_discovery_navigation(self):
        user = User.objects.create_user(username="portal-viewer")
        self.client.force_login(user)
        response = self.client.get(reverse("video_list"))
        self.assertContains(response, 'aria-label="Primary navigation"')
        self.assertContains(response, 'id="site-search"')
