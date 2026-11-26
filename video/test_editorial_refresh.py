from django.test import TestCase
from django.urls import reverse


class EditorialRefreshTests(TestCase):
    def test_discovery_has_browse_and_category_actions(self):
        response = self.client.get(reverse("video_list"))
        self.assertContains(response, 'class="hero-actions"')
        self.assertContains(response, 'href="' + reverse("video_browse") + '">Browse videos</a>')
        self.assertContains(response, 'href="' + reverse("category_list") + '">Explore categories</a>')
