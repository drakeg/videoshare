from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Category, Channel, Video


class CategoryDetailFilteringTests(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(
            username="category-detail-creator",
            password="password123",
        )
        self.channel = Channel.objects.create(
            owner=self.creator,
            name="Category Detail Channel",
            description="Testing category detail filters",
        )
        self.category = Category.objects.create(
            name="Travel",
            description="Travel videos",
        )
        self.other_category = Category.objects.create(name="Food")
        self.url = reverse("category_detail", kwargs={"pk": self.category.pk})

    def video(self, title, *, category=None, views=0, description=None):
        return Video.objects.create(
            title=title,
            description=description or title,
            thumbnail=f"videos/thumbnails/{title}.jpg",
            video_file=f"videos/files/{title}.mp4",
            author=self.creator,
            channel=self.channel,
            category=category or self.category,
            views=views,
        )

    def test_search_is_bounded_and_scoped_to_category(self):
        matching = self.video("Road Adventure", description="Mountain route")
        self.video("City Walk")
        self.video("Road Food", category=self.other_category)

        response = self.client.get(self.url, {"q": "road"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_query"], "road")
        self.assertEqual(list(response.context["videos"].object_list), [matching])

        capped = self.client.get(self.url, {"q": "x" * 180})
        self.assertEqual(len(capped.context["selected_query"]), 120)

    def test_sort_by_views_and_invalid_sort_fallback(self):
        lower = self.video("Lower", views=10)
        higher = self.video("Higher", views=50)

        response = self.client.get(self.url, {"sort": "views"})
        self.assertEqual(list(response.context["videos"].object_list), [higher, lower])
        self.assertEqual(response.context["selected_sort"], "views")

        invalid = self.client.get(self.url, {"sort": "invalid"})
        self.assertEqual(invalid.context["selected_sort"], "newest")

    def test_upload_date_filter_excludes_old_video(self):
        old = self.video("Old")
        recent = self.video("Recent")
        Video.objects.filter(pk=old.pk).update(
            pub_date=timezone.now() - timedelta(days=400)
        )

        response = self.client.get(self.url, {"uploaded": "year"})

        self.assertIn(recent, list(response.context["videos"].object_list))
        self.assertNotIn(old, list(response.context["videos"].object_list))
        self.assertEqual(response.context["selected_upload"], "year")

    def test_category_detail_paginates_at_24(self):
        for number in range(25):
            self.video(f"Travel {number:02d}")

        first = self.client.get(self.url)
        second = self.client.get(self.url, {"page": 2})

        self.assertEqual(len(first.context["videos"]), 24)
        self.assertEqual(first.context["videos"].paginator.num_pages, 2)
        self.assertEqual(len(second.context["videos"]), 1)

    def test_pager_preserves_filters(self):
        for number in range(25):
            self.video(f"Road {number:02d}", views=number)

        response = self.client.get(
            self.url,
            {"q": "road", "uploaded": "year", "sort": "views"},
        )

        self.assertContains(
            response,
            "q=road&amp;uploaded=year&amp;sort=views&amp;page=2",
        )

    def test_visibility_rules_still_apply(self):
        public = self.video("Public")
        private = self.video("Private")
        private.publication_status = Video.PublicationStatus.PRIVATE
        private.save(update_fields=["publication_status"])

        response = self.client.get(self.url)

        self.assertIn(public, list(response.context["videos"].object_list))
        self.assertNotIn(private, list(response.context["videos"].object_list))
