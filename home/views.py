from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from .models import Publication, ResearchProject


def project_detail(request, slug):
    project = get_object_or_404(
        ResearchProject.objects.select_related("area", "image"),
        slug=slug,
        is_published=True,
    )
    publications = project.public_publications
    grants = project.grants.filter(is_published=True)
    members = project.members.filter(is_published=True).select_related("image")
    activities = project.activities.filter(is_published=True).select_related("cover_image")[:4]
    other_projects = (
        ResearchProject.objects.filter(is_published=True)
        .exclude(pk=project.pk)
        .select_related("area", "image")[:3]
    )

    context = {
        "project": project,
        "publications": publications,
        "grants": grants,
        "members": members,
        "activities": activities,
        "other_projects": other_projects,
    }
    return render(request, "home/pages/project_detail.html", context)


def publication_bibtex(request, pk):
    pub = get_object_or_404(Publication.objects.published(), pk=pk)
    response = HttpResponse(pub.bibtex, content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="publication-{pub.pk}.bib"'
    return response
