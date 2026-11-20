from django.test import TestCase
from django.urls import reverse

from .models import Category


class CategoryDirectoryTests(TestCase):
    def setUp(self):
        self.url = reverse("category_list")

    def make_category(self, name, description=""):
        return Category.objects.create(name=name, description=description)

    def test_directory_defaults_to_name_ascending(self):
        zulu = self.make_category("Zulu")
        alpha = self.make_category("Alpha")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["category_sort"], "name")
        self.assertEqual(list(response.context["categories"].object_list), [alpha, zulu])

    def test_name_desc_sort_reverses_directory(self):
        alpha = self.make_category("Alpha")
        zulu = self.make_category("Zulu")

        response = self.client.get(self.url, {"sort": "name_desc"})

        self.assertEqual(response.context["category_sort"], "name_desc")
        self.assertEqual(list(response.context["categories"].object_list), [zulu, alpha])

    def test_invalid_sort_falls_back_to_name(self):
        self.make_category("Zulu")
        self.make_category("Alpha")

        response = self.client.get(self.url, {"sort": "invalid"})

        self.assertEqual(response.context["category_sort"], "name")
        self.assertContains(response, '<option value="name" selected>', html=False)

    def test_search_matches_name_and_description_case_insensitively(self):
        travel = self.make_category("Travel", "Road trips and adventures")
        solar = self.make_category("DIY", "Solar power projects")
        self.make_category("Cooking", "Recipes")

        by_name = self.client.get(self.url, {"q": "TRAV"})
        by_description = self.client.get(self.url, {"q": "solar POWER"})

        self.assertEqual(list(by_name.context["categories"].object_list), [travel])
        self.assertEqual(list(by_description.context["categories"].object_list), [solar])

    def test_search_is_trimmed_capped_and_blank_is_unfiltered(self):
        alpha = self.make_category("Alpha")

        trimmed = self.client.get(self.url, {"q": "  Alpha  "})
        blank = self.client.get(self.url, {"q": "   "})
        capped = self.client.get(self.url, {"q": "x" * 180})

        self.assertEqual(trimmed.context["category_query"], "Alpha")
        self.assertEqual(list(trimmed.context["categories"].object_list), [alpha])
        self.assertEqual(blank.context["category_query"], "")
        self.assertEqual(blank.context["categories"].paginator.count, 1)
        self.assertEqual(len(capped.context["category_query"]), 120)

    def test_directory_paginates_at_24(self):
        for index in range(25):
            self.make_category(f"Category {index:02d}")

        first = self.client.get(self.url)
        second = self.client.get(self.url, {"page": 2})

        self.assertEqual(len(first.context["categories"]), 24)
        self.assertEqual(first.context["categories"].paginator.num_pages, 2)
        self.assertEqual(len(second.context["categories"]), 1)

    def test_pager_preserves_search_and_sort(self):
        for index in range(25):
            self.make_category(f"Trail Category {index:02d}")

        response = self.client.get(self.url, {"q": "trail", "sort": "name_desc"})

        self.assertContains(response, "?q=trail&sort=name_desc&page=2")

    def test_search_form_does_not_preserve_stale_page_number(self):
        response = self.client.get(
            self.url,
            {"q": "trail", "sort": "name_desc", "page": 4},
        )

        self.assertContains(response, 'name="q" value="trail"', html=False)
        self.assertContains(response, 'name="sort"', html=False)
        self.assertNotContains(response, 'name="page"', html=False)

    def test_search_no_results_state_remains_clear(self):
        self.make_category("Travel")

        response = self.client.get(self.url, {"q": "missing"})

        self.assertContains(response, "No categories yet.")
        self.assertEqual(response.context["categories"].paginator.count, 0)
