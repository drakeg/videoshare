import secrets

from django.conf import settings
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()

PILOT_USER_SEARCH_MAX_LENGTH = 100
PILOT_USER_PAGE_SIZE = 50
PILOT_USER_STATUSES = {"all", "active", "suspended"}
PILOT_USER_ONBOARDING_STATUSES = {"all", "never", "signed-in"}




def pilot_user_directory(*, query="", status="all", onboarding="all", page=None):
    normalized_query = (query or "").strip()[:PILOT_USER_SEARCH_MAX_LENGTH]
    normalized_status = status if status in PILOT_USER_STATUSES else "all"
    normalized_onboarding = (
        onboarding if onboarding in PILOT_USER_ONBOARDING_STATUSES else "all"
    )

    queryset = User.objects.filter(is_staff=False, is_superuser=False)
    if normalized_query:
        queryset = queryset.filter(
            Q(username__icontains=normalized_query)
            | Q(email__icontains=normalized_query)
            | Q(first_name__icontains=normalized_query)
            | Q(last_name__icontains=normalized_query)
        )
    if normalized_status == "active":
        queryset = queryset.filter(is_active=True)
    elif normalized_status == "suspended":
        queryset = queryset.filter(is_active=False)

    if normalized_onboarding == "never":
        queryset = queryset.filter(last_login__isnull=True)
    elif normalized_onboarding == "signed-in":
        queryset = queryset.filter(last_login__isnull=False)

    queryset = queryset.order_by("-date_joined", "-pk")
    return (
        Paginator(queryset, PILOT_USER_PAGE_SIZE).get_page(page),
        normalized_query,
        normalized_status,
        normalized_onboarding,
    )

def provision_pilot_user(*, username, email, first_name="", last_name=""):
    """Create an ordinary active user without exposing a temporary password."""
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_active=True,
        is_staff=False,
        is_superuser=False,
    )
    user.set_password(secrets.token_urlsafe(32))
    user.save()
    return user


def password_setup_path(user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return reverse(
        "password_reset_confirm",
        kwargs={"uidb64": uidb64, "token": token},
    )


def send_pilot_user_setup_email(*, user, setup_url, purpose="setup"):
    """Send an opt-in pilot-user setup/reset link through Django's email backend."""
    if not getattr(settings, "PILOT_USER_SETUP_EMAIL_ENABLED", False):
        return "disabled"

    recipient = (user.email or "").strip()
    if not recipient:
        return "missing_email"

    site_name = (getattr(settings, "SITE_NAME", "VideoShare") or "VideoShare").strip()
    display_name = user.get_full_name().strip() or user.username
    if purpose == "reset":
        subject = f"Reset your {site_name} password"
        action = "reset your password"
    else:
        subject = f"Set up your {site_name} account"
        action = "choose your password and finish setting up your account"

    message = (
        f"Hello {display_name},\n\n"
        f"Use this link to {action}:\n{setup_url}\n\n"
        "Treat this link as sensitive. If you were not expecting it, you can ignore this email."
    )
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
    except Exception:
        return "failed"
    return "sent"
