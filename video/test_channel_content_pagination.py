from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .metadata_models import Hashtag, Tag
from .models import Category, Channel, Video
from .shorts_models import VideoShort


class ChannelContentPaginationTests(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username="creator", password="pw")
        self.channel = Channel.objects.create(name="Channel", description="", owner=self.creator)
        self.url = reverse("channel_detail", kwargs={"pk": self.channel.pk})

    def make_video(self, title, *, short=False, **overrides):
        values = {
            "title": title,
            "description": title,
            "thumbnail": f"videos/{title}.jpg",
            "video_file": f"videos/{title}.mp4",
            "author": self.creator,
            "channel": self.channel,
            "publication_status": Video.PublicationStatus.PUBLISHED,
            "audience": Video.Audience.EVERYONE,
        }
        values.update(overrides)
        video = Video.objects.create(**values)
        if short:
            VideoShort.objects.create(video=video)
        return video

    def test_channel_bounds_standard_videos_and_shorts_independently(self):
        for index in range(13):
            self.make_video(f"video-{index}")
        for index in range(9):
            self.make_video(f"short-{index}", short=True)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["videos"]), 12)
        self.assertEqual(response.context["videos"].paginator.num_pages, 2)
        self.assertEqual(len(response.context["shorts"]), 8)
        self.assertEqual(response.context["shorts"].paginator.num_pages, 2)

    def test_each_pagination_link_preserves_the_other_section_page(self):
        for index in range(13):
            self.make_video(f"video-{index}")
        for index in range(9):
            self.make_video(f"short-{index}", short=True)

        response = self.client.get(self.url, {"video_page": 1, "short_page": 1})

        self.assertContains(response, "?video_page=2&short_page=1#channel-videos")
        self.assertContains(response, "?short_page=2&video_page=1#channel-shorts")

    def test_second_pages_return_remaining_content(self):
        for index in range(13):
            self.make_video(f"video-{index}")
        for index in range(9):
            self.make_video(f"short-{index}", short=True)

        response = self.client.get(self.url, {"video_page": 2, "short_page": 2})

        self.assertEqual(len(response.context["videos"]), 1)
        self.assertEqual(len(response.context["shorts"]), 1)
        self.assertContains(response, "Videos page 2 of 2")
        self.assertContains(response, "Shorts page 2 of 2")

    def test_search_matches_title_description_category_tag_and_hashtag(self):
        category = Category.objects.create(name="Travel")
        title_match = self.make_video("Mountain Trail Guide")
        description_match = self.make_video("Workshop", description="RV solar troubleshooting")
        category_match = self.make_video("Category video", category=category)
        tag_match = self.make_video("Tagged video")
        hashtag_match = self.make_video("Hashtag short", short=True)
        noise = self.make_video("Unrelated cooking")
        Tag.objects.create(name="boondocking").videos.add(tag_match)
        Hashtag.objects.create(name="roadlife").videos.add(hashtag_match)

        cases = (
            ("mountain trail", title_match),
            ("SOLAR TROUBLE", description_match),
            ("travel", category_match),
            ("boondock", tag_match),
            ("#roadlife", hashtag_match),
        )
        for query, expected in cases:
            with self.subTest(query=query):
                response = self.client.get(self.url, {"q": query})
                self.assertContains(response, expected.title)
                self.assertNotContains(response, noise.title)

    def test_search_filters_before_both_pagers_and_preserves_query(self):
        for index in range(13):
            self.make_video(f"trail-video-{index}")
        for index in range(9):
            self.make_video(f"trail-short-{index}", short=True)
        self.make_video("unrelated")

        response = self.client.get(self.url, {"q": "trail"})

        self.assertEqual(response.context["videos"].paginator.count, 13)
        self.assertEqual(response.context["videos"].paginator.num_pages, 2)
        self.assertEqual(response.context["shorts"].paginator.count, 9)
        self.assertEqual(response.context["shorts"].paginator.num_pages, 2)
        self.assertContains(response, "?q=trail&video_page=2&short_page=1#channel-videos")
        self.assertContains(response, "?q=trail&short_page=2&video_page=1#channel-shorts")

    def test_search_query_is_trimmed_capped_and_blank_is_unfiltered(self):
        visible = self.make_video("trim target")

        trimmed = self.client.get(self.url, {"q": "  trim target  "})
        self.assertEqual(trimmed.context["channel_query"], "trim target")
        self.assertContains(trimmed, visible.title)

        blank = self.client.get(self.url, {"q": "   "})
        self.assertEqual(blank.context["channel_query"], "")
        self.assertContains(blank, visible.title)

        capped = self.client.get(self.url, {"q": "x" * 180})
        self.assertEqual(len(capped.context["channel_query"]), 120)

    def test_search_never_reveals_non_visible_content(self):
        self.make_video("secret draft", publication_status=Video.PublicationStatus.DRAFT)
        self.make_video("secret draft short", short=True, publication_status=Video.PublicationStatus.DRAFT)

        response = self.client.get(self.url, {"q": "secret draft"})

        self.assertEqual(response.context["videos"].paginator.count, 0)
        self.assertEqual(response.context["shorts"].paginator.count, 0)
        self.assertContains(response, "No channel content matches")
        self.assertNotContains(response, "secret draft short")

    def test_search_form_resets_both_section_pages(self):
        response = self.client.get(
            self.url,
            {"q": "creator", "video_page": 4, "short_page": 3},
        )

        self.assertContains(response, 'name="q" value="creator"', html=False)
        self.assertNotContains(response, 'name="video_page"', html=False)
        self.assertNotContains(response, 'name="short_page"', html=False)

    def test_invalid_page_values_are_handled_safely(self):
        for index in range(13):
            self.make_video(f"video-{index}")
        for index in range(9):
            self.make_video(f"short-{index}", short=True)

        malformed = self.client.get(self.url, {"video_page": "bad", "short_page": "bad"})
        out_of_range = self.client.get(self.url, {"video_page": 999, "short_page": 999})

        self.assertEqual(malformed.context["videos"].number, 1)
        self.assertEqual(malformed.context["shorts"].number, 1)
        self.assertEqual(out_of_range.context["videos"].number, 2)
        self.assertEqual(out_of_range.context["shorts"].number, 2)

    def test_non_visible_content_does_not_enter_pagination(self):
        visible = self.make_video("visible")
        hidden = self.make_video("draft", publication_status=Video.PublicationStatus.DRAFT)
        hidden_short = self.make_video("draft-short", short=True, publication_status=Video.PublicationStatus.DRAFT)

        response = self.client.get(self.url)

        self.assertContains(response, visible.title)
        self.assertNotContains(response, hidden.title)
        self.assertNotContains(response, hidden_short.title)
        self.assertEqual(response.context["videos"].paginator.count, 1)
        self.assertEqual(response.context["shorts"].paginator.count, 0)

    def test_content_is_newest_first_with_deterministic_pk_tie_break(self):
        first = self.make_video("first")
        second = self.make_video("second")
        first_short = self.make_video("first-short", short=True)
        second_short = self.make_video("second-short", short=True)

        response = self.client.get(self.url)

        self.assertEqual(list(response.context["videos"].object_list), [second, first])
        self.assertEqual(list(response.context["shorts"].object_list), [second_short, first_short])
