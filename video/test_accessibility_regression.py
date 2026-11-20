from html.parser import HTMLParser
import re


from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Channel


VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


class HtmlNode:
    def __init__(self, tag, attrs, parent=None):
        self.tag = tag
        self.attrs = dict(attrs)
        self.parent = parent
        self.children = []

    def text_content(self):
        parts = []
        for child in self.children:
            if isinstance(child, str):
                parts.append(child)
            elif child.attrs.get("aria-hidden") != "true":
                if child.tag == "img":
                    parts.append(child.attrs.get("alt", ""))
                else:
                    parts.append(child.text_content())
        return " ".join(" ".join(parts).split())

    def ancestor(self, tag):
        current = self.parent
        while current is not None:
            if current.tag == tag:
                return current
            current = current.parent
        return None


class AccessibilityParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = HtmlNode("document", {})
        self.stack = [self.root]
        self.nodes = []
        self.ids = {}
        self.duplicate_ids = set()

    def handle_starttag(self, tag, attrs):
        node = HtmlNode(tag, attrs, parent=self.stack[-1])
        self.stack[-1].children.append(node)
        self.nodes.append(node)

        node_id = node.attrs.get("id")
        if node_id:
            if node_id in self.ids:
                self.duplicate_ids.add(node_id)
            else:
                self.ids[node_id] = node

        if tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS and self.stack[-1].tag == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if data:
            self.stack[-1].children.append(data)



def relative_luminance(hex_color):
    value = hex_color.lstrip("#")
    channels = [int(value[index:index + 2], 16) / 255 for index in (0, 2, 4)]
    linear = [
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(foreground, background):
    lighter, darker = sorted(
        (relative_luminance(foreground), relative_luminance(background)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def css_color_variables(css):
    return dict(re.findall(r"(--[\w-]+):\s*(#[0-9a-fA-F]{6})\s*;", css))

def accessible_name(node, parser):
    aria_label = node.attrs.get("aria-label", "").strip()
    if aria_label:
        return aria_label

    labelledby = node.attrs.get("aria-labelledby", "").strip()
    if labelledby:
        names = []
        for reference in labelledby.split():
            target = parser.ids.get(reference)
            if target is not None:
                names.append(target.text_content())
        if any(names):
            return " ".join(name for name in names if name).strip()

    if node.tag == "input":
        input_type = node.attrs.get("type", "text").lower()
        if input_type in {"submit", "button", "reset"}:
            value = node.attrs.get("value", "").strip()
            if value:
                return value
        if input_type == "image":
            return node.attrs.get("alt", "").strip()

    return node.text_content().strip()


def form_control_name(node, parser, label_for):
    name = accessible_name(node, parser)
    if name:
        return name

    node_id = node.attrs.get("id")
    if node_id and node_id in label_for:
        return label_for[node_id]

    wrapping_label = node.ancestor("label")
    if wrapping_label is not None:
        return wrapping_label.text_content().strip()

    return ""


def audit_accessibility(html):
    parser = AccessibilityParser()
    parser.feed(html)
    issues = []

    html_nodes = [node for node in parser.nodes if node.tag == "html"]
    if not html_nodes or not html_nodes[0].attrs.get("lang", "").strip():
        issues.append("document must declare a non-empty html lang attribute")

    title_nodes = [node for node in parser.nodes if node.tag == "title"]
    if not title_nodes or not title_nodes[0].text_content().strip():
        issues.append("document must include a non-empty title")

    if parser.duplicate_ids:
        issues.append(
            "duplicate element id(s): " + ", ".join(sorted(parser.duplicate_ids))
        )

    main = parser.ids.get("main-content")
    if main is None or main.tag != "main":
        issues.append("document must include <main id=\"main-content\">")

    skip_links = [
        node
        for node in parser.nodes
        if node.tag == "a"
        and "skip-link" in node.attrs.get("class", "").split()
        and node.attrs.get("href") == "#main-content"
    ]
    if not skip_links or not accessible_name(skip_links[0], parser):
        issues.append("document must include a named skip link to #main-content")

    label_for = {}
    for node in parser.nodes:
        if node.tag == "label":
            target = node.attrs.get("for")
            if target:
                label_for[target] = node.text_content().strip()

    for node in parser.nodes:
        labelledby = node.attrs.get("aria-labelledby", "").strip()
        for reference in labelledby.split():
            if reference not in parser.ids:
                issues.append(
                    f"{node.tag} references missing aria-labelledby id {reference!r}"
                )

        if node.tag == "img" and "alt" not in node.attrs:
            issues.append("img is missing an alt attribute")

        if node.tag in {"a", "button"}:
            if node.attrs.get("aria-hidden") == "true":
                continue
            if node.tag == "a" and not node.attrs.get("href"):
                continue
            if not accessible_name(node, parser):
                issues.append(f"{node.tag} has no accessible name")

        if node.tag in {"input", "select", "textarea"}:
            if node.attrs.get("type", "").lower() == "hidden":
                continue
            if not form_control_name(node, parser, label_for):
                identifier = node.attrs.get("id") or node.attrs.get("name") or "<unnamed>"
                issues.append(
                    f"{node.tag} {identifier!r} has no accessible label/name"
                )

    return issues


class AccessibilityAuditorUnitTests(TestCase):
    def test_auditor_detects_common_structural_failures(self):
        issues = audit_accessibility(
            """
            <html><head><title></title></head><body>
              <a class="skip-link" href="#main-content"></a>
              <main id="main-content"></main>
              <img src="/x.png">
              <button><svg aria-hidden="true"></svg></button>
              <input id="email" name="email">
              <div id="dup"></div><div id="dup"></div>
              <section aria-labelledby="missing"></section>
            </body></html>
            """
        )

        joined = "\n".join(issues)
        self.assertIn("html lang", joined)
        self.assertIn("non-empty title", joined)
        self.assertIn("duplicate element id", joined)
        self.assertIn("missing an alt", joined)
        self.assertIn("button has no accessible name", joined)
        self.assertIn("input 'email' has no accessible label/name", joined)
        self.assertIn("missing aria-labelledby", joined)

    def test_auditor_accepts_named_and_labelled_controls(self):
        issues = audit_accessibility(
            """
            <!doctype html>
            <html lang="en"><head><title>Good page</title></head><body>
              <a class="skip-link" href="#main-content">Skip</a>
              <main id="main-content">
                <label for="email">Email</label><input id="email" name="email">
                <button aria-label="Search"><svg aria-hidden="true"></svg></button>
                <a href="/home"><img src="/home.png" alt="Home"></a>
              </main>
            </body></html>
            """
        )

        self.assertEqual(issues, [])

    def test_core_design_tokens_meet_normal_text_contrast_floor(self):
        stylesheet_path = finders.find("style.css")
        self.assertIsNotNone(stylesheet_path)
        with open(stylesheet_path, encoding="utf-8") as stylesheet:
            css = stylesheet.read()

        colors = css_color_variables(css)
        for foreground, background in (
            ("--ink", "--canvas"),
            ("--ink-soft", "--canvas"),
            ("--accent-deep", "--canvas"),
            ("--accent-deep", "--surface"),
            ("--danger", "--surface"),
            ("--success", "--surface"),
        ):
            with self.subTest(foreground=foreground, background=background):
                self.assertGreaterEqual(
                    contrast_ratio(colors[foreground], colors[background]),
                    4.5,
                )

        self.assertRegex(
            css,
            r"\.side-nav-label\s*\{[^}]*color:\s*var\(--ink-soft\)",
            msg="small side-nav section labels must use the accessible secondary text token",
        )


class RenderedAccessibilityRegressionTests(TestCase):
    def assert_accessible_response(self, response, *, route_name):
        self.assertEqual(
            response.status_code,
            200,
            msg=f"{route_name} should render before accessibility auditing",
        )
        issues = audit_accessibility(response.content.decode(response.charset or "utf-8"))
        self.assertEqual(
            issues,
            [],
            msg=f"{route_name} accessibility issues:\n" + "\n".join(issues),
        )

    def test_core_anonymous_pages_pass_structural_accessibility_gate(self):
        for route_name in (
            "video_list",
            "video_browse",
            "channel_list",
            "category_list",
            "shorts_feed",
            "login",
            "register",
        ):
            with self.subTest(route_name=route_name):
                self.assert_accessible_response(
                    self.client.get(reverse(route_name)),
                    route_name=route_name,
                )

    def test_search_results_page_passes_structural_accessibility_gate(self):
        response = self.client.get(reverse("search"), {"query": "accessibility"})
        self.assert_accessible_response(response, route_name="search")

    def test_authenticated_creator_upload_passes_structural_accessibility_gate(self):
        user = User.objects.create_user(username="creator", password="password123")
        Channel.objects.create(
            owner=user,
            name="Accessible Creator",
            description="Creator channel",
            thumbnail="channels/accessible.jpg",
        )
        self.client.force_login(user)

        self.assert_accessible_response(
            self.client.get(reverse("upload")),
            route_name="upload",
        )

    @override_settings(PRIVATE_PORTAL=True, ALLOW_PUBLIC_REGISTRATION=False)
    def test_private_portal_redirect_lands_on_accessible_login_page(self):
        response = self.client.get(reverse("video_list"), follow=True)

        self.assertEqual(response.redirect_chain[-1][0].split("?")[0], reverse("login"))
        self.assert_accessible_response(response, route_name="private-portal-login")
