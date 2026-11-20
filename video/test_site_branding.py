from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Channel, Playlist


class SiteBrandingTests(TestCase):
    def test_default_brand_remains_videoshare(self):
        response = self.client.get(reverse("video_list"))

        self.assertContains(response, "<title>Discover · VideoShare</title>", html=True)
        self.assertContains(response, 'aria-label="VideoShare home"', html=False)
        self.assertContains(response, 'placeholder="Search VideoShare"', count=2, html=False)

    @override_settings(SITE_NAME="Acme Training TV")
    def test_custom_brand_updates_shared_shell_and_page_title(self):
        response = self.client.get(reverse("video_list"))

        self.assertContains(response, "<title>Discover · Acme Training TV</title>", html=True)
        self.assertContains(response, 'aria-label="Acme Training TV home"', html=False)
        self.assertContains(response, 'placeholder="Search Acme Training TV"', count=2, html=False)
        self.assertContains(response, ">Acme Training TV</span>", html=False)

    @override_settings(SITE_NAME="Acme Training TV")
    def test_custom_brand_updates_auth_copy(self):
        response = self.client.get(reverse("register"))

        self.assertContains(response, "<title>Register · Acme Training TV</title>", html=True)
        self.assertContains(response, "Join Acme Training TV")

    @override_settings(SITE_NAME="Acme Training TV")
    def test_custom_brand_updates_default_channel_and_playlist_copy(self):
        owner = User.objects.create_user(username="owner", password="password123")
        channel = Channel.objects.create(owner=owner, name="Acme Channel", description="")
        playlist = Playlist.objects.create(
            owner=owner,
            name="Starter Library",
            description="",
            visibility=Playlist.Visibility.PUBLIC,
        )

        channel_response = self.client.get(reverse("channel_detail", kwargs={"pk": channel.pk}))
        playlist_response = self.client.get(reverse("playlist_detail", kwargs={"pk": playlist.pk}))

        self.assertContains(channel_response, "A Acme Training TV channel.")
        self.assertContains(playlist_response, "A Acme Training TV collection.")
