from django.db import models

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.snippets.models import register_snippet


DEFAULT_RESEARCH_AREAS = """Environmental sustainability
Waste valorization
Resource recovery
Environmental engineering"""


class PublicationQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Publication.Status.PUBLISHED)


@register_snippet
class Publication(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    class PublicationType(models.TextChoices):
        JOURNAL = "journal", "Journal Article"
        CONFERENCE = "conference", "Conference Paper"
        BOOK_CHAPTER = "book_chapter", "Book Chapter"
        PREPRINT = "preprint", "Preprint / Working Paper"
        REPORT = "report", "Technical Report"

    title = models.CharField(max_length=300)
    authors = models.TextField(help_text="List authors in publication order.")
    year = models.PositiveSmallIntegerField(db_index=True)
    venue = models.CharField(
        "Journal or conference",
        max_length=300,
        blank=True,
    )
    doi = models.CharField(
        "DOI",
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        help_text="Optional. Enter the DOI only; each DOI must be unique.",
    )
    publication_type = models.CharField(
        max_length=20,
        choices=PublicationType.choices,
        default=PublicationType.JOURNAL,
        db_index=True,
    )
    publication_url = models.URLField("Publication URL", blank=True)
    abstract = models.TextField(blank=True)
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    featured = models.BooleanField(default=False)

    objects = PublicationQuerySet.as_manager()

    panels = [
        FieldPanel("title"),
        FieldPanel("authors"),
        FieldPanel("year"),
        FieldPanel("publication_type"),
        FieldPanel("venue"),
        FieldPanel("doi"),
        FieldPanel("publication_url"),
        FieldPanel("abstract"),
        MultiFieldPanel(
            [FieldPanel("status"), FieldPanel("featured")],
            heading="Visibility",
        ),
    ]

    class Meta:
        ordering = ["-year", "title"]

    def __str__(self):
        return f"{self.title} ({self.year})"

    @property
    def bibtex(self):
        first_author = "author"
        if self.authors:
            cleaned = self.authors.replace("et al.", "").replace("et al", "")
            first_person = cleaned.split(",")[0].strip()
            parts = first_person.split()
            if parts:
                first_author = parts[-1].lower()
        first_word = "work"
        if self.title:
            words = [w.lower() for w in self.title.split() if w.isalnum()]
            if words:
                first_word = words[0]
        cite_key = f"{first_author}{self.year}{first_word}"

        entry_type = {
            self.PublicationType.JOURNAL: "article",
            self.PublicationType.CONFERENCE: "inproceedings",
            self.PublicationType.BOOK_CHAPTER: "incollection",
            self.PublicationType.PREPRINT: "misc",
            self.PublicationType.REPORT: "techreport",
        }.get(self.publication_type, "article")

        lines = [f"@{entry_type}{{{cite_key},"]
        lines.append(f"  title = {{{self.title}}},")
        lines.append(f"  author = {{{self.authors}}},")
        lines.append(f"  year = {{{self.year}}},")
        if self.venue:
            field_name = "journal" if entry_type == "article" else "booktitle"
            lines.append(f"  {field_name} = {{{self.venue}}},")
        if self.doi:
            lines.append(f"  doi = {{{self.doi}}},")
        if self.publication_url:
            lines.append(f"  url = {{{self.publication_url}}},")
        lines.append("}")
        return "\n".join(lines)

    def clean(self):
        super().clean()
        if self.doi is not None:
            self.doi = self.doi.strip() or None

    def save(self, *args, **kwargs):
        if self.doi is not None:
            self.doi = self.doi.strip() or None
        super().save(*args, **kwargs)


class HomePage(Page):
    hero_headline = models.CharField(
        max_length=120,
        blank=True,
        help_text="Lab name displayed in the centered page header.",
    )
    hero_subtitle = models.TextField(
        blank=True,
        help_text="Mission statement displayed in the dark band below the research image.",
    )
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional panoramic research photograph displayed below the navigation.",
    )
    lab_introduction = RichTextField(
        blank=True,
        features=["bold", "italic", "link"],
        help_text="Introduction displayed in the Team and Research showcase.",
    )
    team_member_count = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Optional verified count displayed in the homepage Team showcase.",
    )
    research_areas = models.TextField(
        blank=True,
        default=DEFAULT_RESEARCH_AREAS,
        help_text="Enter one research area per line.",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_headline"),
                FieldPanel("hero_subtitle"),
                FieldPanel("hero_image"),
            ],
            heading="Hero",
        ),
        FieldPanel("lab_introduction", heading="About the lab"),
        MultiFieldPanel(
            [FieldPanel("team_member_count"), FieldPanel("research_areas")],
            heading="Homepage statistics",
        ),
    ]

    @property
    def configured_research_areas(self):
        return [area.strip() for area in self.research_areas.splitlines() if area.strip()]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        from .content_models import Grant, NewsArticlePage, ResearchProject
        context["publication_count"] = Publication.objects.published().count()
        context["research_areas"] = self.configured_research_areas
        context["project_count"] = ResearchProject.objects.filter(is_published=True).count()
        context["grant_count"] = Grant.objects.filter(is_published=True).count()
        context["featured_projects"] = ResearchProject.objects.filter(is_published=True).select_related("area", "image")[:3]
        context["recent_publications"] = Publication.objects.published().order_by("-year", "-pk")[:4]
        context["featured_grants"] = Grant.objects.filter(is_published=True).select_related("related_project").order_by("sort_order", "-start_date")[:4]
        context["latest_news"] = NewsArticlePage.objects.live().public().select_related("cover_image").order_by("-date", "-pk")[:3]
        return context


class SectionPage(Page):
    intro = models.TextField(blank=True)
    heading = models.CharField(max_length=160, blank=True, help_text="Optional display heading; the navigation title stays unchanged.")
    body = RichTextField(blank=True, help_text="Supporting introduction, research approach, or collaboration information.")
    feature_image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    image_caption = models.CharField(max_length=250, blank=True)
    methodology = RichTextField(blank=True, help_text="Monitoring methods, equipment, collection and analysis. Enter only verified details.")

    parent_page_types = ["home.HomePage"]
    subpage_types = ["home.NewsArticlePage"]

    content_panels = Page.content_panels + [
        FieldPanel("heading"), FieldPanel("intro"), FieldPanel("body"),
        MultiFieldPanel([FieldPanel("feature_image"), FieldPanel("image_caption")], heading="Editorial image"),
        FieldPanel("methodology"),
    ]

    def get_template(self, request, *args, **kwargs):
        from .page_context import SECTION_TEMPLATES
        return SECTION_TEMPLATES.get(self.slug, "home/section_page.html")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        from .page_context import section_context
        context.update(section_context(self, request))
        return context


# Split editorial records from the established homepage and publication models.
from .content_models import Activity, ActivityImage, Grant, NewsArticlePage, ResearchArea, ResearchProject, TeamMember  # noqa: E402,F401
