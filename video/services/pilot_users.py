import secrets

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


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
