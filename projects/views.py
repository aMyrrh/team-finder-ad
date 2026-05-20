import json
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from team_finder.utils import paginate_queryset

from .forms import ProjectForm
from .models import Project


def project_list_view(request):
    projects = Project.objects.select_related("owner").all()
    page_obj = paginate_queryset(request, projects)
    return render(request, "projects/project_list.html", {
        "page_obj": page_obj,
        "projects": projects,
        "query_prefix": "",
    })


def project_detail_view(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        pk=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project_view(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        return redirect("projects:detail", project_id=project.id)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("projects:detail", project_id=project.id)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
@require_POST
def complete_project_view(request, project_id):
    project = Project.objects.filter(pk=project_id, owner=request.user).first()
    if project is None:
        return JsonResponse({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)
    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok"})


@login_required
@require_POST
def toggle_participate_view(request, project_id):
    project = Project.objects.filter(pk=project_id).first()
    if project is None:
        return JsonResponse({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)
    user = request.user
    if user == project.owner:
        return JsonResponse({"error": "Owner cannot participate"}, status=HTTPStatus.BAD_REQUEST)
    is_participant = project.participants.filter(id=user.id).exists()
    if is_participant:
        project.participants.remove(user)
    else:
        project.participants.add(user)
    return JsonResponse({"status": "ok", "participant": not is_participant})
