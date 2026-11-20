from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.urls import Resolver404, resolve, reverse


PUBLIC_AUTH_URL_NAMES = {
    "login",
    "register",
    "password_reset",
    "password_reset_done",
    "password_reset_confirm",
    "password_reset_complete",
}


class PrivatePortalMiddleware:
    """Require login for site content when the opt-in private portal mode is enabled."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.PRIVATE_PORTAL or request.user.is_authenticated:
            return self.get_response(request)

        if self._is_public_path(request):
            return self.get_response(request)

        return redirect_to_login(
            request.get_full_path(),
            login_url=reverse("login"),
        )

    @staticmethod
    def _is_public_path(request):
        path = request.path_info

        static_url = settings.STATIC_URL or "/static/"
        if static_url.startswith("/") and path.startswith(static_url):
            return True

        try:
            match = resolve(path)
        except Resolver404:
            return False

        if match.namespace == "admin":
            return True

        return match.url_name in PUBLIC_AUTH_URL_NAMES
