from collections import Counter
from dataclasses import dataclass
from typing import Sequence

from django.db.models import Count, F, Max, Q, QuerySet

from video.models import Playlist, Video


DISCOVERY_SECTION_LIMIT = 4
PERSONALIZATION_HISTORY_LIMIT = 20
TOPIC_SIGNAL_LIMIT = 6
RECOMMENDATION_CANDIDATE_LIMIT = 200


@dataclass(frozen=True)
class TopicSignal:
    kind: str
    name: str
    count: int


@dataclass(frozen=True)
class DiscoverySections:
    newest_videos: QuerySet
    most_viewed_videos: QuerySet
    most_liked_videos: QuerySet
    shorts_videos: QuerySet
    recently_watched_videos: QuerySet
    continue_watching_videos: QuerySet
    followed_channel_videos: QuerySet
    recommended_videos: Sequence[Video]
    topic_signals: tuple[TopicSignal, ...]
    public_playlists: QuerySet


def _personalized_sections(user, videos, limit):
    watched_ids = list(
        user.watch_history.order_by("-watched_at").values_list("video_id", flat=True)[:PERSONALIZATION_HISTORY_LIMIT]
    )
    followed = (
        videos.filter(channel__subscribers=user)
        .exclude(pk__in=watched_ids)
        .order_by("-pub_date", "-pk")[:limit]
    )
    if not watched_ids:
        return followed, Video.objects.none(), ()

    watched = list(
        Video.objects.filter(pk__in=watched_ids)
        .select_related("category")
        .prefetch_related("tags", "hashtags")
    )
    category_counts = Counter(video.category_id for video in watched if video.category_id)
    channel_counts = Counter(video.channel_id for video in watched if video.channel_id)
    tag_counts = Counter(tag.name for video in watched for tag in video.tags.all())
    hashtag_counts = Counter(tag.name for video in watched for tag in video.hashtags.all())

    category_ids = tuple(category_counts)
    channel_ids = tuple(channel_counts)
    tag_names = tuple(tag_counts)
    hashtag_names = tuple(hashtag_counts)
    topic_filter = Q()
    if category_ids:
        topic_filter |= Q(category_id__in=category_ids)
    if channel_ids:
        topic_filter |= Q(channel_id__in=channel_ids)
    if tag_names:
        topic_filter |= Q(tags__name__in=tag_names)
    if hashtag_names:
        topic_filter |= Q(hashtags__name__in=hashtag_names)

    recommended = ()
    if topic_filter:
        candidates = list(
            videos.filter(topic_filter)
            .exclude(pk__in=watched_ids)
            .annotate(like_count=Count("likes", distinct=True))
            .prefetch_related("tags", "hashtags")
            .order_by("-pub_date", "-pk")[:RECOMMENDATION_CANDIDATE_LIMIT]
        )

        for candidate in candidates:
            candidate_tag_names = {tag.name for tag in candidate.tags.all()}
            candidate_hashtag_names = {tag.name for tag in candidate.hashtags.all()}
            candidate.topic_score = (
                category_counts.get(candidate.category_id, 0) * 3
                + channel_counts.get(candidate.channel_id, 0) * 2
                + len(candidate_tag_names.intersection(tag_names)) * 2
                + len(candidate_hashtag_names.intersection(hashtag_names)) * 2
            )

        candidates.sort(
            key=lambda candidate: (
                candidate.topic_score,
                candidate.like_count,
                candidate.views,
                candidate.pub_date,
                candidate.pk,
            ),
            reverse=True,
        )
        recommended = tuple(candidates[:limit])

    signals = []
    for name, count in tag_counts.items():
        signals.append(TopicSignal("tag", name, count))
    for name, count in hashtag_counts.items():
        signals.append(TopicSignal("hashtag", name, count))
    signals.sort(key=lambda signal: (-signal.count, signal.kind, signal.name))
    return followed, recommended, tuple(signals[:TOPIC_SIGNAL_LIMIT])


def get_discovery_sections(user, limit=DISCOVERY_SECTION_LIMIT):
    all_videos = Video.objects.visible_to(user).select_related("author", "category", "channel")
    videos = all_videos.filter(short_metadata__isnull=True)
    shorts = all_videos.filter(short_metadata__isnull=False)
    recently_watched = Video.objects.none()
    continue_watching = Video.objects.none()
    followed_channel_videos = Video.objects.none()
    recommended_videos = Video.objects.none()
    topic_signals = ()

    if user.is_authenticated:
        recently_watched = (
            videos.filter(history_entries__user=user)
            .annotate(last_watched_at=Max("history_entries__watched_at"))
            .order_by("-last_watched_at", "-pk")[:limit]
        )
        continue_watching = (
            videos.filter(
                history_entries__user=user,
                history_entries__playback_position_seconds__gt=0,
                history_entries__duration_seconds__gt=0,
            )
            .annotate(
                resume_position_seconds=F("history_entries__playback_position_seconds"),
                playback_duration_seconds=F("history_entries__duration_seconds"),
                remaining_seconds=(F("history_entries__duration_seconds") - F("history_entries__playback_position_seconds")),
                last_watched_at=Max("history_entries__watched_at"),
            )
            .filter(remaining_seconds__gt=5)
            .order_by("-last_watched_at", "-pk")[:limit]
        )
        followed_channel_videos, recommended_videos, topic_signals = _personalized_sections(user, videos, limit)

    return DiscoverySections(
        newest_videos=videos.order_by("-pub_date", "-pk")[:limit],
        most_viewed_videos=videos.order_by("-views", "-pub_date", "-pk")[:limit],
        most_liked_videos=(
            videos.annotate(like_count=Count("likes", distinct=True))
            .order_by("-like_count", "-views", "-pub_date", "-pk")[:limit]
        ),
        shorts_videos=shorts.order_by("-pub_date", "-pk")[:limit],
        recently_watched_videos=recently_watched,
        continue_watching_videos=continue_watching,
        followed_channel_videos=followed_channel_videos,
        recommended_videos=recommended_videos,
        topic_signals=topic_signals,
        public_playlists=(
            Playlist.objects.filter(visibility=Playlist.Visibility.PUBLIC)
            .select_related("owner")
            .annotate(video_count=Count("items", distinct=True))
            .order_by("-updated_at", "name", "-pk")[:limit]
        ),
    )
