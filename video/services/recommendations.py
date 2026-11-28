from django.db.models import Case, Exists, IntegerField, OuterRef, Q, Value, When

from ..metadata_models import Hashtag, Tag

from ..models import Video


WATCH_RECOMMENDATION_LIMIT = 8


def watch_recommendations(video, user, limit=WATCH_RECOMMENDATION_LIMIT):
    """Return a small deterministic set of visible long-form videos to watch next."""
    limit = max(0, min(int(limit), WATCH_RECOMMENDATION_LIMIT))
    if limit == 0:
        return Video.objects.none()

    candidates = (
        Video.objects.visible_to(user)
        .filter(short_metadata__isnull=True)
        .exclude(pk=video.pk)
        .select_related("author", "channel", "category")
    )

    same_category = Q(pk__isnull=True)
    if video.category_id:
        same_category = Q(category_id=video.category_id)

    same_channel = Q(pk__isnull=True)
    if video.channel_id:
        same_channel = Q(channel_id=video.channel_id)

    # EXISTS avoids multiplying candidate rows across multiple matching topics.
    shared_tags = Tag.objects.filter(
        pk__in=video.tags.values("pk"), videos=OuterRef("pk")
    )
    shared_hashtags = Hashtag.objects.filter(
        pk__in=video.hashtags.values("pk"), videos=OuterRef("pk")
    )
    candidates = candidates.annotate(
        shared_tag=Exists(shared_tags),
        shared_hashtag=Exists(shared_hashtags),
    ).annotate(
        recommendation_rank=Case(
            When(shared_tag=True, shared_hashtag=True, then=Value(0)),
            When(Q(shared_tag=True) | Q(shared_hashtag=True), then=Value(1)),
            When(same_category, then=Value(2)),
            When(same_channel, then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by("recommendation_rank", "-pub_date", "-pk")

    return candidates[:limit]
