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
        active_projects = ResearchProject.objects.filter(
            is_published=True,
            status=ResearchProject.Status.ACTIVE
        ).select_related("area", "image")
        context["active_projects"] = active_projects
        context["projects"] = active_projects
        context["related_publications"] = Publication.objects.published().filter(projects__is_published=True).distinct()[:3]
        context["research_grants"] = Grant.objects.filter(is_published=True).select_related("related_project").order_by("sort_order", "-start_date")[:4]
    elif page.slug == "grants":
        records = Grant.objects.filter(is_published=True).select_related("related_project")
        context["has_grants"] = records.exists()
        active = [g for g in records if g.is_active_grant]
        previous = [g for g in records if not g.is_active_grant]
        context["active_grants"] = active
        context["previous_grants"] = previous
        context["lab_grants"] = [g for g in records if g.category == Grant.Category.LAB]
        context["director_grants"] = [g for g in records if g.category == Grant.Category.DIRECTOR]
        context["collab_grants"] = [g for g in records if g.category == Grant.Category.COLLABORATION]
        context["grants"] = records
    elif page.slug == "team":
        members = list(TeamMember.objects.filter(is_published=True).select_related("image"))
        directors = [m for m in members if m.category == "director"]
        context["directors"] = directors
        context["director"] = directors[0] if directors else None

        # Current Research Assistants
        context["assistants"] = [m for m in members if m.category == "assistant"]

        # Other Contributors: published non-director, non-assistant, non-alumni
        context["other_contributors"] = [
            m for m in members
            if m.category not in ("director", "assistant", "alumni")
        ]

        # Alumni
        context["alumni"] = [m for m in members if m.category == "alumni"]

        # Featured members for interactive portrait accordion fallback
        featured = [m for m in members if getattr(m, "is_featured", False)]
        if not featured and len(members) >= 3:
            featured = members[:5]

        # Enable preview mode for interactive accordion inspection if requested
        if (not featured or len(featured) < 3) and request.GET.get("preview") in ("accordion", "team", "1"):
            class SampleMember:
                def __init__(self, pk, name, role, cat, affil, bg, deg, email=""):
                    self.pk = pk
                    self.name = name
                    self.role = role
                    self.category = cat
                    self.affiliation = affil
                    self.research_interests = bg
                    self.academic_background = deg
                    self.biography = f"{name} conducts research at Waste Mining Lab, exploring sustainable recovery pathways and environmental bioengineering."
                    self.image = None
                    self.email = email
                    self.profile_url = ""
                    self.scholar_url = ""
                    self.linkedin_url = ""
                    self.alumni_current_position = ""
                    self.public_projects = []
                    self.is_director_fallback = (cat == "director")

                def get_category_display(self):
                    return {"director": "Lab Director", "scientist": "Research Scientist", "assistant": "Research Assistant"}.get(self.category, "Researcher")

                @property
                def initials(self):
                    parts = [p for p in self.name.replace("Dr.", "").strip().split() if p]
                    return f"{parts[0][0]}{parts[-1][0]}".upper() if len(parts) > 1 else "WML"

            sample_1 = SampleMember(101, "Dr. Asef Mohammad Redwan", "Principal Investigator & Assistant Professor", "director", "North South University", "Microbial bioremediation, rare earth elements recovery, immobilized packed bed bio-reactors.", "Ph.D. Environmental Engineering", "asef.redwan@northsouth.edu")
            sample_2 = SampleMember(102, "Tanvir Ahmed Chowdhury", "Senior Research Associate", "scientist", "Waste Mining Lab · NSU", "Bio-electrochemical systems, industrial wastewater treatment, and zero liquid discharge modeling.", "M.Sc. Environmental Science & Tech", "t.chowdhury@example.com")
            sample_3 = SampleMember(103, "Farzana Yeasmin", "Graduate Research Assistant", "assistant", "Department of CEE · NSU", "AI-powered vision models for municipal solid waste characterization and circular bioeconomy streams.", "B.Sc. Civil & Environmental Eng.", "f.yeasmin@example.com")
            featured = [sample_1, sample_2, sample_3]

        context["featured_members"] = featured

        # Categorized members for structured academic directory
        context["scientists"] = [m for m in members if m.category in ("scientist", "researcher")]
        context["staff"] = [m for m in members if m.category == "staff"]
        context["students"] = [m for m in members if m.category == "student"]
        context["collaborators"] = [m for m in members if m.category == "collaborator"]

        context["member_groups"] = [{"label": label, "members": [member for member in members if member.category == key]} for key, label in TeamMember.Category.choices if key != "director"]
        context["has_members"] = any(member.category != "director" for member in members)
        context["all_members"] = members
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
