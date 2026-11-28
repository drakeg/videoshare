import re

# Only locally served static image files; no remote tracking or arbitrary URLs.
_BRAND_IMAGE = re.compile(r"^branding/(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+\.(?:png|webp|jpg|jpeg|ico)$", re.IGNORECASE)


def brand_image_path(value):
    value = str(value or "").strip()
    return value if _BRAND_IMAGE.fullmatch(value) else ""
