from django.conf import settings
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import RegistrationForm


class RegistrationView(CreateView):
    template_name = "registration/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("login")

    def dispatch(self, request, *args, **kwargs):
        if not settings.ALLOW_PUBLIC_REGISTRATION:
            return HttpResponseForbidden("Public registration is disabled.")
        return super().dispatch(request, *args, **kwargs)
