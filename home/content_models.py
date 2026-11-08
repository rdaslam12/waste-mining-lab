"""Editorial content for secondary pages; new records stay private by default."""
from django.db import models
from django.db.models import Q
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.snippets.models import register_snippet


class PublicRecord(models.Model):
    is_published = models.BooleanField(default=False, help_text="Show publicly after the content has been verified.")
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ["sort_order", "pk"]


@register_snippet
class ResearchArea(PublicRecord):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    panels = [FieldPanel("title"), FieldPanel("description"), FieldPanel("image"), FieldPanel("sort_order"), FieldPanel("is_published")]

    def __str__(self):
        return self.title


@register_snippet
class ResearchProject(PublicRecord, ClusterableModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active research"
        COMPLETED = "completed", "Completed"
        PLANNED = "planned", "Planned inquiry"

    title = models.CharField(max_length=250)
    slug = models.SlugField(
        max_length=250,
        blank=True,
        null=True,
        unique=True,
        help_text="Slug for project detail page (e.g., 'textile-wastewater-treatment').",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    summary = models.TextField()
    area = models.ForeignKey(ResearchArea, null=True, blank=True, on_delete=models.SET_NULL, related_name="projects")
    image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = RichTextField(blank=True)
    methodology = RichTextField(blank=True, help_text="Detailed scientific methodology, experimental design, and equipment.")
    collaborations = models.TextField(blank=True, help_text="Partner institutions, agencies, or industry partners.")
    funding_notes = models.TextField(blank=True, help_text="Associated grant support and funding information.")
    external_url = models.URLField(blank=True)
    publications = ParentalManyToManyField("home.Publication", blank=True, related_name="projects")
    monitoring_related = models.BooleanField(default=False, help_text="Also feature this project on Waste Monitoring.")

    panels = [
        FieldPanel("title"),
        FieldPanel("slug"),
        FieldPanel("status"),
        FieldPanel("summary"),
        FieldPanel("area"),
        FieldPanel("image"),
        MultiFieldPanel(
            [
                FieldPanel("start_date"),
                FieldPanel("end_date"),
                FieldPanel("collaborations"),
                FieldPanel("funding_notes"),
            ],
            heading="Project timeline & Collaboration",
        ),
        FieldPanel("description"),
        FieldPanel("methodology"),
        FieldPanel("external_url"),
        FieldPanel("publications"),
        FieldPanel("monitoring_related"),
        FieldPanel("sort_order"),
        FieldPanel("is_published"),
    ]

    @property
    def public_publications(self):
        return self.publications.published()

    def get_absolute_url(self):
        if self.slug:
            return f"/research/{self.slug}/"
        return f"/research/#project-{self.pk}"

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            from django.utils.text import slugify
            base_slug = slugify(self.title)[:200]
            candidate = base_slug
            idx = 1
            while ResearchProject.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{idx}"
                idx += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


@register_snippet
class Grant(PublicRecord, ClusterableModel):
    class Category(models.TextChoices):
        LAB = "lab", "Laboratory funding"
        DIRECTOR = "director_affiliated", "Director-associated grants"
        PREVIOUS = "previous_institutional", "Previous institutional funding"
        COLLABORATION = "collaboration", "Research collaborations"

    title = models.CharField(max_length=300)
    funding_organization = models.CharField(max_length=255)
    amount_display = models.CharField(
        max_length=100,
        blank=True,
        help_text="Formatted funding amount (e.g., 'BDT 14 Lakh', 'USD 898,265').",
    )
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Numeric amount if available.",
    )
    currency = models.CharField(max_length=10, blank=True, default="BDT")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    role = models.CharField(
        max_length=120,
        default="Principal Investigator (PI)",
        help_text="Role such as Principal Investigator (PI) or Co-PI.",
    )
    awarded_institution = models.CharField(
        max_length=255,
        blank=True,
        help_text="Awarded or administering institution (e.g., North South University, ITN-BUET, Idaho National Laboratory).",
    )
    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.LAB,
        db_index=True,
        help_text="Distinguish lab-direct, director-associated, or prior institutional funding.",
    )
    related_project = models.ForeignKey(
        ResearchProject,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="grants",
    )
    summary = models.TextField(blank=True, help_text="Summary of grant objectives and scope.")
    public_source_url = models.URLField(blank=True, help_text="Public verification URL.")
    is_verified = models.BooleanField(
        default=True,
        help_text="Verified against public university or agency records.",
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("funding_organization"),
        MultiFieldPanel(
            [FieldPanel("amount_display"), FieldPanel("amount"), FieldPanel("currency")],
            heading="Funding amount",
        ),
        MultiFieldPanel(
            [
                FieldPanel("start_date"),
                FieldPanel("end_date"),
                FieldPanel("role"),
                FieldPanel("awarded_institution"),
                FieldPanel("category"),
            ],
            heading="Award details & Classification",
        ),
        FieldPanel("related_project"),
        FieldPanel("summary"),
        FieldPanel("public_source_url"),
        MultiFieldPanel(
            [FieldPanel("is_verified"), FieldPanel("is_published"), FieldPanel("sort_order")],
            heading="Verification & Visibility",
        ),
    ]

    class Meta:
        ordering = ["sort_order", "-start_date", "-pk"]
        verbose_name_plural = "Grants & Funding"

    def __str__(self):
        return f"{self.title} ({self.funding_organization})"

    @property
    def period_display(self):
        if self.start_date and self.end_date:
            return f"{self.start_date.strftime('%B %Y')} – {self.end_date.strftime('%B %Y')}"
        elif self.start_date:
            return f"From {self.start_date.strftime('%B %Y')}"
        elif self.end_date:
            return f"Until {self.end_date.strftime('%B %Y')}"
        return ""

    @property
    def is_active_grant(self):
        if self.related_project:
            if self.related_project.status == ResearchProject.Status.ACTIVE:
                return True
            if self.related_project.status == ResearchProject.Status.COMPLETED:
                return False
        if self.end_date:
            from datetime import date
            return self.end_date >= date.today()
        if self.category == self.Category.PREVIOUS:
            return False
        return False


@register_snippet
class TeamMember(PublicRecord, ClusterableModel):
    class Category(models.TextChoices):
        DIRECTOR = "director", "Principal Investigator / Lab Director"
        SCIENTIST = "scientist", "Research Scientists & Postdoctoral Researchers"
        ASSISTANT = "assistant", "Research Assistants"
        STUDENT = "student", "Graduate & Undergraduate Researchers"
        STAFF = "staff", "Research Officers & Laboratory Staff"
        COLLABORATOR = "collaborator", "Collaborators & Co-Researchers"
        ALUMNI = "alumni", "Alumni / Former Members"
        # Backward compatibility with existing records
        RESEARCHER = "researcher", "Researchers"

    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, blank=True, help_text="Slug for profile modal/anchor (e.g., 'asef-redwan').")
    role = models.CharField(max_length=200, help_text="Academic or research designation.")
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.ASSISTANT)
    affiliation = models.CharField(max_length=200, blank=True, help_text="Department, center, or university affiliation.")
    academic_background = models.CharField(max_length=255, blank=True, help_text="Degrees / academic qualifications (e.g., B.Sc. in Civil & Environmental Eng., NSU).")
    biography = models.TextField(blank=True, help_text="Short biography / background summary.")
    research_interests = models.TextField(blank=True, help_text="Comma-separated or narrative research focus.")
    image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    is_featured = models.BooleanField(default=False, help_text="Feature in the interactive portrait accordion on the Team page.")
    email = models.EmailField(blank=True)
    profile_url = models.URLField(blank=True, help_text="Faculty or institutional profile link.")
    linkedin_url = models.URLField(blank=True, help_text="LinkedIn profile URL.")
    scholar_url = models.URLField(blank=True, help_text="Google Scholar profile URL.")
    alumni_current_position = models.CharField(max_length=255, blank=True, help_text="For alumni: current position and affiliation (e.g., Graduate Researcher, Stanford).")
    projects = ParentalManyToManyField(ResearchProject, blank=True, related_name="members")

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("role"),
        FieldPanel("category"),
        FieldPanel("affiliation"),
        FieldPanel("academic_background"),
        FieldPanel("biography"),
        FieldPanel("research_interests"),
        FieldPanel("image"),
        FieldPanel("is_featured"),
        MultiFieldPanel(
            [
                FieldPanel("email"),
                FieldPanel("profile_url"),
                FieldPanel("linkedin_url"),
                FieldPanel("scholar_url"),
            ],
            heading="Contact & Academic Links",
        ),
        FieldPanel("alumni_current_position"),
        FieldPanel("projects"),
        FieldPanel("sort_order"),
        FieldPanel("is_published"),
    ]

    @property
    def public_projects(self):
        return self.projects.filter(is_published=True)

    @property
    def initials(self):
        parts = [p for p in self.name.replace("Dr.", "").replace("Prof.", "").strip().split() if p]
        if not parts:
            return "WML"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return f"{parts[0][0]}{parts[-1][0]}".upper()

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            from django.utils.text import slugify
            base_slug = slugify(self.name)[:140]
            candidate = base_slug
            idx = 1
            while TeamMember.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{idx}"
                idx += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


@register_snippet
class Activity(PublicRecord, ClusterableModel):
    class Category(models.TextChoices):
        FIELD = "field", "Field visits"
        LAB = "laboratory", "Laboratory activities"
        WORKSHOP = "workshop", "Workshops"
        SEMINAR = "seminar", "Seminars"
        PRESENTATION = "presentation", "Research presentations"
        OUTREACH = "outreach", "Outreach & collaborations"

    title = models.CharField(max_length=250)
    date = models.DateField()
    category = models.CharField(max_length=20, choices=Category.choices)
    description = RichTextField()
    cover_image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    external_url = models.URLField(blank=True)
    project = models.ForeignKey(ResearchProject, null=True, blank=True, on_delete=models.SET_NULL, related_name="activities")
    featured = models.BooleanField(default=False)
    panels = [FieldPanel(name) for name in ["title", "date", "category", "description", "cover_image", "external_url", "project", "featured", "is_published"]] + [InlinePanel("gallery_images", label="Gallery photograph")]

    class Meta:
        ordering = ["-date", "-pk"]
        verbose_name_plural = "Activities"

    def __str__(self):
        return self.title

    @property
    def archive_url(self):
        """Keep cross-page links valid even when this entry is on an older page."""
        newer = Activity.objects.filter(is_published=True).filter(
            Q(date__gt=self.date) | Q(date=self.date, pk__gt=self.pk)
        ).count()
        page_number = newer // 10 + 1
        query = f"?page={page_number}" if page_number > 1 else ""
        return f"/activity/{query}#activity-{self.pk}"


class ActivityImage(Orderable):
    activity = ParentalKey(Activity, on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ForeignKey("wagtailimages.Image", on_delete=models.CASCADE, related_name="+")
    caption = models.CharField(max_length=250, blank=True)
    panels = [FieldPanel("image"), FieldPanel("caption")]


class NewsArticlePage(Page):
    class Category(models.TextChoices):
        ANNOUNCEMENT = "announcement", "Announcements"
        RESEARCH = "research", "Research updates"
        LAB = "lab", "Lab news"

    date = models.DateField()
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.LAB)
    excerpt = models.TextField(max_length=500)
    cover_image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    body = RichTextField()
    featured = models.BooleanField(default=False)
    related_project = models.ForeignKey(ResearchProject, null=True, blank=True, on_delete=models.SET_NULL, related_name="news_articles")
    related_publication = models.ForeignKey("home.Publication", null=True, blank=True, on_delete=models.SET_NULL, related_name="news_articles")
    related_activity = models.ForeignKey(Activity, null=True, blank=True, on_delete=models.SET_NULL, related_name="news_articles")

    template = "home/pages/news_article.html"
    parent_page_types = ["home.SectionPage"]
    subpage_types = []
    content_panels = Page.content_panels + [FieldPanel(name) for name in ["date", "category", "excerpt", "cover_image", "body", "featured"]] + [MultiFieldPanel([FieldPanel("related_project"), FieldPanel("related_publication"), FieldPanel("related_activity")], heading="Related verified content")]

    @classmethod
    def can_exist_under(cls, parent):
        return super().can_exist_under(parent) and parent.slug == "news"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["related_news"] = NewsArticlePage.objects.child_of(self.get_parent()).live().public().exclude(pk=self.pk).order_by("-date", "-pk")[:3]
        return context
