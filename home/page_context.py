"""Small, route-specific queries without changing existing Wagtail page types."""
from django.core.paginator import Paginator
from django.db.models import Q

SECTION_TEMPLATES = {slug: f"home/pages/{slug.replace('-', '_')}.html" for slug in (
    "publications", "research", "team", "activity", "news", "waste-monitoring", "contact", "grants"
)}

AREA_DESCRIPTIONS = {
    "Environmental sustainability": "Understanding environmental systems to inform more thoughtful use of materials, water and natural resources.",
    "Waste valorization": "Exploring how discarded materials can become useful inputs, and how their value can be understood.",
    "Resource recovery": "Investigating opportunities to recover valuable resources from waste and environmental systems.",
    "Environmental engineering": "Connecting engineering principles with environmental processes to explore practical approaches to complex challenges.",
}


def paginate(records, request, context, per_page=12):
    context["paginator_page"] = Paginator(records, per_page).get_page(request.GET.get("page"))
    query = request.GET.copy()
    query.pop("page", None)
    context["filter_query"] = query.urlencode()
    return context["paginator_page"].object_list


def section_context(page, request):
    from .models import Activity, Grant, HomePage, NewsArticlePage, Publication, ResearchArea, ResearchProject, TeamMember

    context = {}
    if page.slug == "publications":
        records = Publication.objects.published()
        context["years"] = records.order_by("-year").values_list("year", flat=True).distinct()
        context["has_publications"] = records.exists()
        query = request.GET.get("q", "").strip()[:200]
        year = request.GET.get("year", "").strip()[:10]
        pub_type = request.GET.get("type", "").strip()[:30]
        context.update(query=query, selected_year=year, selected_type=pub_type)
        context["publication_types"] = Publication.PublicationType.choices
        if query:
            records = records.filter(Q(title__icontains=query) | Q(authors__icontains=query) | Q(venue__icontains=query) | Q(abstract__icontains=query) | Q(doi__icontains=query))
        if year:
            records = records.filter(year=int(year)) if year.isascii() and year.isdigit() and 0 < int(year) <= 32767 else records.none()
        if pub_type:
            records = records.filter(publication_type=pub_type)
        context["featured_publications"] = records.filter(featured=True)[:2] if not query and not year and not pub_type else []
        context["publications"] = paginate(records, request, context)
    elif page.slug == "research":
        areas = ResearchArea.objects.filter(is_published=True).select_related("image")
        if not areas.exists():
            home = page.get_parent().specific
            labels = home.configured_research_areas if isinstance(home, HomePage) else []
            areas = [{"title": label, "description": AREA_DESCRIPTIONS.get(label, "")} for label in labels]
        context["areas"] = areas
        context["projects"] = ResearchProject.objects.filter(is_published=True).select_related("area", "image")
        context["related_publications"] = Publication.objects.published().filter(projects__is_published=True).distinct()[:3]
        context["research_grants"] = Grant.objects.filter(is_published=True).select_related("related_project").order_by("sort_order", "-start_date")[:4]
    elif page.slug == "grants":
        records = Grant.objects.filter(is_published=True).select_related("related_project")
        context["has_grants"] = records.exists()
        context["lab_grants"] = [g for g in records if g.category == Grant.Category.LAB]
        context["director_grants"] = [g for g in records if g.category == Grant.Category.DIRECTOR]
        context["previous_grants"] = [g for g in records if g.category == Grant.Category.PREVIOUS]
        context["collab_grants"] = [g for g in records if g.category == Grant.Category.COLLABORATION]
        context["grants"] = records
    elif page.slug == "team":
        members = list(TeamMember.objects.filter(is_published=True).select_related("image"))
        context["directors"] = [member for member in members if member.category == "director"]
        context["member_groups"] = [{"label": label, "members": [member for member in members if member.category == key]} for key, label in TeamMember.Category.choices if key != "director"]
        context["has_members"] = any(member.category != "director" for member in members)
    elif page.slug == "activity":
        records = Activity.objects.filter(is_published=True).select_related("cover_image", "project").prefetch_related("gallery_images__image")
        context["featured_activity"] = records.filter(featured=True).first()
        context["activities"] = paginate(records, request, context, 10)
        context["activity_categories"] = Activity.Category.labels
    elif page.slug == "news":
        records = NewsArticlePage.objects.child_of(page).live().public().select_related("cover_image").order_by("-date", "-pk")
        context["has_news"] = records.exists()
        category = request.GET.get("category", "")[:30]
        context["categories"] = NewsArticlePage.Category.choices
        context["selected_category"] = category
        if category:
            records = records.filter(category=category)
        context["featured_story"] = records.filter(featured=True).first() if not category else None
        context["articles"] = paginate(records, request, context)
    elif page.slug == "waste-monitoring":
        context["projects"] = ResearchProject.objects.filter(is_published=True, monitoring_related=True).select_related("area", "image")
        context["related_publications"] = Publication.objects.published().filter(projects__is_published=True, projects__monitoring_related=True).distinct()[:3]
    return context
