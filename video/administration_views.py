import csv

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .community_models import CommunityPost, CommunityReply
from .models import Channel, Video
from .pilot_user_forms import PilotUserCsvImportForm, PilotUserProvisioningForm
from .services.administration import get_creator_audience, get_site_admin_overview, moderate_site_comment
from .services.pilot_user_import import PilotUserCsvValidationError, validate_pilot_user_csv
from .services.pilot_users import password_setup_path, pilot_user_directory, provision_pilot_user, send_pilot_user_setup_email
from .services.moderation_actions import (
    restore_video,
    set_channel_suspended,
    set_community_post_hidden,
    set_community_reply_hidden,
    set_user_active,
    take_down_video,
)

User = get_user_model()


@staff_member_required
def site_admin_dashboard(request):
    return render(request, "videos/site_admin_dashboard.html", get_site_admin_overview())


def _pilot_user_context(request, *, form=None, import_form=None, setup_user=None, setup_url=None, setup_heading=None, setup_description=None, email_delivery_status=None):
    email_enabled = getattr(settings, "PILOT_USER_SETUP_EMAIL_ENABLED", False)
    pilot_users, pilot_user_query, pilot_user_status = pilot_user_directory(
        query=request.GET.get("q", ""),
        status=request.GET.get("status", "all"),
        page=request.GET.get("page"),
    )
    return {
        "form": form or PilotUserProvisioningForm(email_delivery_enabled=email_enabled),
        "import_form": import_form or PilotUserCsvImportForm(),
        "pilot_users": pilot_users,
        "pilot_user_query": pilot_user_query,
        "pilot_user_status": pilot_user_status,
        "setup_user": setup_user,
        "setup_url": setup_url,
        "setup_heading": setup_heading,
        "setup_description": setup_description,
        "email_delivery_status": email_delivery_status,
        "pilot_setup_email_enabled": email_enabled,
    }


@staff_member_required
def site_admin_pilot_users(request):
    email_enabled = getattr(settings, "PILOT_USER_SETUP_EMAIL_ENABLED", False)
    form = PilotUserProvisioningForm(
        request.POST or None,
        email_delivery_enabled=email_enabled,
    )
    if request.method == "POST" and form.is_valid():
        user = provision_pilot_user(
            username=form.cleaned_data["username"],
            email=form.cleaned_data["email"],
            first_name=form.cleaned_data.get("first_name", ""),
            last_name=form.cleaned_data.get("last_name", ""),
        )
        setup_url = request.build_absolute_uri(password_setup_path(user))
        email_delivery_status = None
        if form.cleaned_data.get("send_setup_email"):
            email_delivery_status = send_pilot_user_setup_email(
                user=user,
                setup_url=setup_url,
                purpose="setup",
            )
        return render(
            request,
            "videos/site_admin_pilot_users.html",
            _pilot_user_context(
                request,
                setup_user=user,
                setup_url=setup_url,
                setup_heading=f"Account created for @{user.username}",
                setup_description=(
                    "Share this password-setup link through your approved channel. "
                    "Treat it as sensitive until the user chooses a password."
                ),
                email_delivery_status=email_delivery_status,
            ),
        )

    return render(
        request,
        "videos/site_admin_pilot_users.html",
        _pilot_user_context(request, form=form),
    )


@staff_member_required
@require_POST
def site_admin_pilot_user_csv_import(request):
    import_form = PilotUserCsvImportForm(request.POST, request.FILES)
    if not import_form.is_valid():
        return render(
            request,
            "videos/site_admin_pilot_users.html",
            _pilot_user_context(request, import_form=import_form),
            status=400,
        )

    try:
        rows = validate_pilot_user_csv(import_form.cleaned_data["csv_file"])
    except PilotUserCsvValidationError as error:
        for message in error.messages:
            import_form.add_error("csv_file", message)
        return render(
            request,
            "videos/site_admin_pilot_users.html",
            _pilot_user_context(request, import_form=import_form),
            status=400,
        )

    with transaction.atomic():
        users = [provision_pilot_user(**row) for row in rows]

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="pilot-user-setup-links.csv"'
    writer = csv.writer(response)
    writer.writerow(["username", "email", "setup_url"])
    for user in users:
        writer.writerow(
            [
                user.username,
                user.email,
                request.build_absolute_uri(password_setup_path(user)),
            ]
        )
    return response


@staff_member_required
@require_POST
def site_admin_pilot_user_reset_link(request, pk):
    user = get_object_or_404(
        User,
        pk=pk,
        is_staff=False,
        is_superuser=False,
        is_active=True,
    )
    setup_url = request.build_absolute_uri(password_setup_path(user))
    email_delivery_status = None
    if request.POST.get("delivery") == "email":
        email_delivery_status = send_pilot_user_setup_email(
            user=user,
            setup_url=setup_url,
            purpose="reset",
        )
    return render(
        request,
        "videos/site_admin_pilot_users.html",
        _pilot_user_context(
            request,
            setup_user=user,
            setup_url=setup_url,
            setup_heading=f"Reset link generated for @{user.username}",
            setup_description=(
                "Share this reset/setup link through your approved channel. "
                "It does not change the user's current password until they submit a new one."
            ),
            email_delivery_status=email_delivery_status,
        ),
    )


@staff_member_required
@require_POST
def site_admin_channel_moderate(request, pk):
    channel = get_object_or_404(Channel, pk=pk)
    action = request.POST.get("action", "")
    if action not in {"suspend", "restore"}:
        return HttpResponseBadRequest("Invalid moderation action.")
    try:
        set_channel_suspended(actor=request.user, channel=channel, suspended=action == "suspend", reason=request.POST.get("reason", ""))
    except ValueError as error:
        return HttpResponseBadRequest(str(error))
    return redirect("site_admin_dashboard")


@staff_member_required
@require_POST
def site_admin_comment_moderate(request, pk):
    action = request.POST.get("action", "")
    try:
        found = moderate_site_comment(actor=request.user, comment_id=pk, action=action, reason=request.POST.get("reason", ""))
    except ValueError as error:
        return HttpResponseBadRequest(str(error))
    if not found: raise Http404("Comment not found")
    return redirect("site_admin_dashboard")


@staff_member_required
@require_POST
def site_admin_video_moderate(request, pk):
    video = get_object_or_404(Video, pk=pk); action = request.POST.get("action", ""); reason = request.POST.get("reason", "")
    try:
        if action == "hide": take_down_video(actor=request.user, video=video, reason=reason)
        elif action == "restore": restore_video(actor=request.user, video=video, reason=reason)
        else: return HttpResponseBadRequest("Invalid moderation action.")
    except ValueError as error: return HttpResponseBadRequest(str(error))
    return redirect("site_admin_dashboard")


@staff_member_required
@require_POST
def site_admin_user_moderate(request, pk):
    user = get_object_or_404(User, pk=pk); action = request.POST.get("action", "")
    try:
        if action == "suspend": set_user_active(actor=request.user, user=user, active=False, reason=request.POST.get("reason", ""))
        elif action == "reactivate": set_user_active(actor=request.user, user=user, active=True, reason=request.POST.get("reason", ""))
        else: return HttpResponseBadRequest("Invalid moderation action.")
    except ValueError as error: return HttpResponseBadRequest(str(error))
    return redirect("site_admin_dashboard")


@staff_member_required
@require_POST
def site_admin_community_post_moderate(request, pk):
    post = get_object_or_404(CommunityPost, pk=pk); action = request.POST.get("action", "")
    if action not in {"hide", "restore"}: return HttpResponseBadRequest("Invalid moderation action.")
    try: set_community_post_hidden(actor=request.user, post=post, hidden=action == "hide", reason=request.POST.get("reason", ""))
    except ValueError as error: return HttpResponseBadRequest(str(error))
    return redirect("site_admin_dashboard")


@staff_member_required
@require_POST
def site_admin_community_reply_moderate(request, pk):
    reply = get_object_or_404(CommunityReply, pk=pk); action = request.POST.get("action", "")
    if action not in {"hide", "restore"}: return HttpResponseBadRequest("Invalid moderation action.")
    try: set_community_reply_hidden(actor=request.user, reply=reply, hidden=action == "hide", reason=request.POST.get("reason", ""))
    except ValueError as error: return HttpResponseBadRequest(str(error))
    return redirect("site_admin_dashboard")


@login_required
def creator_audience(request):
    channels = get_creator_audience(request.user)
    if not channels: raise Http404("No owned channels")
    return render(request, "videos/creator_audience.html", {"channel_audiences": channels})
