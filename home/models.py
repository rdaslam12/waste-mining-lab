from django.db import models

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel


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
        help_text="Introduction displayed in the research section below the mission.",
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
    ]
class SectionPage(Page):
    intro = models.TextField(blank=True)

    parent_page_types = ["home.HomePage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]