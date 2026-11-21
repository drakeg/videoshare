from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from video.models import Video


CATEGORY_VIDEO_SORTS = {
    "newest": "Newest",
    "views": "Most viewed",
    "likes": "Most liked",
}

CATEGORY_UPLOAD_FILTERS = {
    "any": "Any time",
    "today": "Today",
    "week": "This week",
    "month": "This month",
    "year": "This year",
}


def _upload_date_start(uploaded):
    if uploaded == "any":
        return None
    now = timezone.localtime(timezone.now())
    if uploaded == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if uploaded == "week":
        return now - timedelta(days=7)
    if uploaded == "month":
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if uploaded == "year":
        return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    return None


def get_category_videos(user, category, *, query="", sort="newest", uploaded="any"):
    selected_query = (query or "").strip()[:120]
    selected_sort = sort if sort in CATEGORY_VIDEO_SORTS else "newest"
    selected_upload = uploaded if uploaded in CATEGORY_UPLOAD_FILTERS else "any"

    videos = (
        Video.objects.visible_to(user)
        .filter(category=category)
        .select_related("author", "channel", "category")
        .prefetch_related("hashtags")
    )

    if selected_query:
        videos = videos.filter(
            Q(title__icontains=selected_query)
            | Q(description__icontains=selected_query)
            | Q(author__username__icontains=selected_query)
            | Q(channel__name__icontains=selected_query)
        )

    upload_start = _upload_date_start(selected_upload)
    if upload_start is not None:
        videos = videos.filter(pub_date__gte=upload_start)

    if selected_sort == "views":
        videos = videos.order_by("-views", "-pub_date", "-pk")
    elif selected_sort == "likes":
        videos = videos.annotate(like_count=Count("likes", distinct=True)).order_by(
            "-like_count", "-views", "-pub_date", "-pk"
        )
    else:
        videos = videos.order_by("-pub_date", "-pk")

    return videos, selected_query, selected_sort, selected_upload
