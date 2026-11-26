from django.conf import settings
from django.utils import timezone

from .models import Channel
from .services.channels import accessible_channels
from .services.notifications import deliver_due_scheduled_upload_notifications


def unread_notifications(request):
    # Scheduled publishing is request-time based, so use the same low-cost model
    # for in-app upload notifications. The service is idempotent and bounded;
    # the management command remains available for deterministic catch-up.
    deliver_due_scheduled_upload_notifications(limit=10)

    count = 0
    is_creator = False
    owns_channel = False
    pending_team_invitation_count = 0
    if request.user.is_authenticated:
        count = request.user.notifications.filter(read_at__isnull=True).count()
        is_creator = accessible_channels(request.user).exists()
        owns_channel = Channel.objects.filter(owner=request.user).exists()
        pending_team_invitation_count = request.user.channel_team_invitations.filter(
            status="pending", expires_at__gt=timezone.now()
        ).count()
    return {
        "unread_notification_count": count,
        "is_creator": is_creator,
        "owns_channel": owns_channel,
        "pending_team_invitation_count": pending_team_invitation_count,
    }


def site_branding(request):
    return {
        "site_name": settings.SITE_NAME,
        "brand_site_name": settings.SITE_NAME,
        "site_tagline": settings.SITE_TAGLINE,
        "home_headline": settings.HOME_HEADLINE,
        "home_subtitle": settings.HOME_SUBTITLE,
    }


def registration_policy(request):
    return {
        "public_registration_enabled": settings.ALLOW_PUBLIC_REGISTRATION,
        "private_portal_enabled": settings.PRIVATE_PORTAL,
    }
