import json
from http import HTTPStatus

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from team_finder.utils import paginate_queryset

from .forms import EditProfileForm, LoginForm, RegisterForm
from .models import Skill, User

SKILLS_AUTOCOMPLETE_LIMIT = 10


def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("users:login")
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.cleaned_data["user"])
        return redirect("projects:list")
    return render(request, "users/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_detail_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": user})


@login_required
def edit_profile_view(request):
    form = EditProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("users:detail", user_id=request.user.id)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password_view(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("users:detail", user_id=request.user.id)
    return render(request, "users/change_password.html", {"form": form})


def users_list_view(request):
    active_skill = request.GET.get("skill", "").strip()
    users_qs = User.objects.all()
    if active_skill:
        users_qs = users_qs.filter(skills__name=active_skill)
    all_skills = Skill.objects.values_list("name", flat=True).order_by("name")

    page_obj = paginate_queryset(request, users_qs)

    query_prefix = f"skill={active_skill}&" if active_skill else ""

    return render(request, "users/participants.html", {
        "page_obj": page_obj,
        "all_skills": all_skills,
        "active_skill": active_skill,
        "query_prefix": query_prefix,
    })


def skills_autocomplete(request):
    query = request.GET.get("q", "").strip()
    skills_qs = Skill.objects.all()
    if query:
        skills_qs = skills_qs.filter(name__icontains=query)
    skills_qs = skills_qs[:SKILLS_AUTOCOMPLETE_LIMIT]
    return JsonResponse(
        [{"id": skill.id, "name": skill.name} for skill in skills_qs],
        safe=False,
    )


@login_required
def user_skill_add(request, user_id):
    if request.user.id != user_id:
        return JsonResponse({"error": "Forbidden"}, status=HTTPStatus.FORBIDDEN)
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=HTTPStatus.METHOD_NOT_ALLOWED)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)

    skill_id = data.get("skill_id")
    name = data.get("name", "").strip()

    if skill_id:
        skill = Skill.objects.filter(pk=skill_id).first()
        if skill is None:
            return JsonResponse({"error": "Skill not found"}, status=HTTPStatus.NOT_FOUND)
    elif name:
        skill, _ = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({"error": "skill_id or name required"}, status=HTTPStatus.BAD_REQUEST)

    request.user.skills.add(skill)
    return JsonResponse({"id": skill.id, "name": skill.name})


@login_required
def user_skill_remove(request, user_id, skill_id):
    if request.user.id != user_id:
        return JsonResponse({"error": "Forbidden"}, status=HTTPStatus.FORBIDDEN)
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=HTTPStatus.METHOD_NOT_ALLOWED)

    skill = Skill.objects.filter(pk=skill_id).first()
    if skill is None:
        return JsonResponse({"error": "Skill not found"}, status=HTTPStatus.NOT_FOUND)
    request.user.skills.remove(skill)
    return JsonResponse({"ok": True})
