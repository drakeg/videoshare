from django.test import TestCase, override_settings
from django.urls import reverse


class WhiteLabelBrandingTests(TestCase):
    @override_settings(
        SITE_NAME="Acme Training TV",
        SITE_TAGLINE="Training that travels with your team.",
        HOME_HEADLINE="Everything your crew needs to learn.",
        HOME_SUBTITLE="Private, branded video training for field teams and managers.",
    )
    def test_homepage_renders_customer_branding(self):
        response = self.client.get(reverse("video_list"))

        self.assertContains(response, "Acme Training TV")
        self.assertContains(response, "Training that travels with your team.")
        self.assertContains(response, "Everything your crew needs to learn.")
        self.assertContains(response, "Private, branded video training for field teams and managers.")
        self.assertContains(
            response,
            '<meta name="description" content="Training that travels with your team.">',
            html=True,
        )

    @override_settings(
        SITE_TAGLINE="Customer portal",
        HOME_HEADLINE="Customer videos",
        HOME_SUBTITLE="A customer-specific video library.",
    )
    def test_branding_context_is_available_outside_homepage(self):
        response = self.client.get(reverse("channel_list"))

        self.assertEqual(response.context["site_tagline"], "Customer portal")
        self.assertEqual(response.context["home_headline"], "Customer videos")
        self.assertEqual(response.context["home_subtitle"], "A customer-specific video library.")

    @override_settings(SITE_LOGO="branding/acme/logo.png", SITE_FAVICON="branding/acme/icon.ico")
    def test_custom_assets_render_on_home_and_login(self):
        for route in ("video_list", "login"):
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertContains(response, "/static/branding/acme/logo.png")
                self.assertContains(response, "/static/branding/acme/icon.ico")
                self.assertContains(response, 'class="brand-logo"')

    @override_settings(SITE_LOGO="https://example.com/logo.png", SITE_FAVICON="branding/../icon.ico")
    def test_unsafe_assets_fall_back_to_defaults(self):
        response = self.client.get(reverse("video_list"))
        self.assertNotContains(response, "https://example.com/logo.png")
        self.assertContains(response, "/static/video/favicon.svg")
        self.assertContains(response, 'class="brand-mark"')

    @override_settings(SITE_LOGO="", SITE_FAVICON="")
    def test_default_assets_are_preserved(self):
        response = self.client.get(reverse("video_list"))
        self.assertContains(response, "/static/video/favicon.svg")
        self.assertContains(response, 'class="brand-mark"')
