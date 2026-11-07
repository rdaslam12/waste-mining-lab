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
    title = models.CharField(max_length=250)
    summary = models.TextField()
    area = models.ForeignKey(ResearchArea, null=True, blank=True, on_delete=models.SET_NULL, related_name="projects")
    image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    description = RichTextField(blank=True)
    external_url = models.URLField(blank=True)
    publications = ParentalManyToManyField("home.Publication", blank=True, related_name="projects")
    monitoring_related = models.BooleanField(default=False, help_text="Also feature this project on Waste Monitoring.")
    panels = [FieldPanel("title"), FieldPanel("summary"), FieldPanel("area"), FieldPanel("image"), FieldPanel("description"), FieldPanel("external_url"), FieldPanel("publications"), FieldPanel("monitoring_related"), FieldPanel("sort_order"), FieldPanel("is_published")]

    @property
    def public_publications(self):
        return self.publications.published()

    def __str__(self):
        return self.title


@register_snippet
class TeamMember(PublicRecord, ClusterableModel):
    class Category(models.TextChoices):
        DIRECTOR = "director", "Laboratory director"
        RESEARCHER = "researcher", "Researchers"
        STUDENT = "student", "Students"
        COLLABORATOR = "collaborator", "Collaborators"
        ALUMNI = "alumni", "Alumni"

    name = models.CharField(max_length=150)
    role = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.RESEARCHER)
    affiliation = models.CharField(max_length=200, blank=True)
    biography = models.TextField(blank=True)
    research_interests = models.TextField(blank=True)
    image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    email = models.EmailField(blank=True)
    profile_url = models.URLField(blank=True)
    projects = ParentalManyToManyField(ResearchProject, blank=True, related_name="members")
    panels = [FieldPanel(name) for name in ["name", "role", "category", "affiliation", "biography", "research_interests", "image", "email", "profile_url", "projects", "sort_order", "is_published"]]

    @property
    def public_projects(self):
        return self.projects.filter(is_published=True)

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
