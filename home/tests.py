from home.models import HomePage, Publication, SectionPage

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.urls import reverse

from wagtail.images import get_image_model
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase


class HomeSetUpTests(WagtailPageTestCase):
    """
    Tests for basic page structure setup and HomePage creation.
    """

    def test_root_create(self):
        root_page = Page.objects.get(pk=1)
        self.assertIsNotNone(root_page)

    def test_homepage_create(self):
        root_page = Page.objects.get(pk=1)
        homepage = HomePage(title="Home")
        root_page.add_child(instance=homepage)
        self.assertTrue(HomePage.objects.filter(title="Home").exists())


class HomeTests(WagtailPageTestCase):
    """
    Tests for homepage functionality and rendering.
    """

    def setUp(self):
        """
        Create a homepage instance for testing.
        """
        root_page = Page.get_first_root_node()
        Site.objects.create(hostname="testsite", root_page=root_page, is_default_site=True)
        self.homepage = HomePage(title="Home")
        root_page.add_child(instance=self.homepage)

    def test_homepage_is_renderable(self):
        self.assertPageIsRenderable(self.homepage)

    def test_homepage_template_used(self):
        response = self.client.get(self.homepage.url)
        self.assertTemplateUsed(response, "home/home_page.html")

    def test_homepage_uses_content_fallbacks(self):
        response = self.client.get(self.homepage.url)

        self.assertContains(response, "Waste Mining Lab")
        self.assertContains(response, "At Waste Mining Lab, we explore")
        self.assertContains(response, "Turning waste into <em>value.</em>", html=True)
        self.assertContains(response, "Recovering resources.")
        self.assertContains(response, "Rethinking waste for a")
        self.assertContains(response, "hero image has not yet been selected")
        self.assertContains(response, "Dr. Asef M. Redwan")
        self.assertContains(response, "Research Areas")
        self.assertNotContains(response, 'class="lab-introduction"')

    def test_homepage_uses_pinned_hero_assets_without_featured_grid(self):
        response = self.client.get(self.homepage.url)

        self.assertContains(response, "css/wml-pinned-hero.css")
        self.assertContains(response, "js/wml-pinned-hero.js")
        self.assertNotContains(response, "wml-featured.css")
        self.assertNotContains(response, "wml-featured.js")
        self.assertNotContains(response, 'class="wml-featured"')

    def test_homepage_renders_editable_content(self):
        self.homepage.hero_headline = "Recovering value from waste"
        self.homepage.hero_subtitle = "A custom research summary."
        self.homepage.lab_introduction = "<p>A custom lab introduction.</p>"
        self.homepage.save_revision().publish()

        response = self.client.get(self.homepage.url)

        self.assertContains(response, "A custom research summary.")
        self.assertContains(response, "A custom lab introduction.")
        self.homepage.refresh_from_db()
        self.assertEqual(self.homepage.hero_headline, "Recovering value from waste")

    def test_wagtail_admin_can_open_homepage_editor(self):
        editor = get_user_model().objects.create_superuser(
            username="lab-editor",
            email="editor@example.com",
            password="test-password",
        )
        self.client.force_login(editor)

        response = self.client.get(
            reverse("wagtailadmin_pages:edit", args=[self.homepage.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hero headline")
        self.assertContains(response, "Hero subtitle")
        self.assertContains(response, "Hero image")
        self.assertContains(response, 'name="lab_introduction"')
        self.assertContains(response, 'name="team_member_count"')
        self.assertContains(response, 'name="research_areas"')

    def test_hero_image_is_optional(self):
        self.assertIsNone(self.homepage.hero_image)

    def test_hero_image_can_be_assigned(self):
        image = get_image_model().objects.create(
            title="Recovered material sample",
            description="Recovered material samples prepared for analysis.",
            file=SimpleUploadedFile(
                "sample.gif",
                (
                    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
                    b"\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00"
                    b"\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
                ),
                content_type="image/gif",
            ),
        )

        def delete_test_image_files():
            for rendition in image.renditions.all():
                rendition.file.delete(save=False)
            image.file.delete(save=False)

        self.addCleanup(delete_test_image_files)
        self.homepage.hero_image = image
        self.homepage.save_revision().publish()

        self.assertEqual(self.homepage.hero_image.title, "Recovered material sample")
        response = self.client.get(self.homepage.url)
        self.assertContains(
            response,
            'alt="Recovered material samples prepared for analysis."',
        )
        self.assertContains(response, "fill-800x1000")
        self.assertContains(response, "fill-1600x1000")
        self.assertContains(response, "fill-2400x1400")


class PublicationTests(WagtailPageTestCase):
    def setUp(self):
        root_page = Page.get_first_root_node()
        self.homepage = HomePage(title="Publications test home", slug="publications-home")
        root_page.add_child(instance=self.homepage)
        self.publications_page = SectionPage(
            title="Publications",
            slug="publications",
            intro="Research outputs from Waste Mining Lab.",
        )
        self.homepage.add_child(instance=self.publications_page)
        Site.objects.create(
            hostname="publications.test",
            root_page=self.homepage,
            is_default_site=True,
        )

    def create_publication(self, **overrides):
        values = {
            "title": "Resource recovery from wastewater",
            "authors": "A. Researcher and B. Scientist",
            "year": 2026,
            "venue": "Environmental Research Journal",
            "status": Publication.Status.PUBLISHED,
        }
        values.update(overrides)
        return Publication.objects.create(**values)

    def test_publication_can_be_created(self):
        publication = self.create_publication(
            doi="10.1000/wml.1",
            publication_url="https://example.org/publication",
            abstract="A concise abstract.",
            featured=True,
        )

        self.assertEqual(str(publication), "Resource recovery from wastewater (2026)")
        self.assertTrue(publication.featured)

    def test_publications_page_shows_only_published_records_newest_first(self):
        self.create_publication(title="Older published work", year=2024)
        self.create_publication(title="Newest published work", year=2026)
        self.create_publication(
            title="Unpublished draft",
            year=2027,
            status=Publication.Status.DRAFT,
        )

        response = self.client.get(self.publications_page.url)

        self.assertContains(response, "Newest published work")
        self.assertContains(response, "Older published work")
        self.assertNotContains(response, "Unpublished draft")
        self.assertLess(
            response.content.index(b"Newest published work"),
            response.content.index(b"Older published work"),
        )

    def test_doi_must_be_unique_when_provided(self):
        self.create_publication(doi="10.1000/wml.unique")

        duplicate = Publication(
            title="Duplicate DOI in admin form",
            authors="A. Researcher",
            year=2026,
            doi=" 10.1000/wml.unique ",
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

        with self.assertRaises(IntegrityError), transaction.atomic():
            self.create_publication(
                title="Duplicate DOI",
                doi="10.1000/wml.unique",
            )

    def test_multiple_publications_can_have_no_doi(self):
        self.create_publication(title="First publication without DOI", doi=None)
        self.create_publication(title="Second publication without DOI", doi="")

        self.assertEqual(Publication.objects.count(), 2)

    def test_homepage_publication_count_uses_only_published_records(self):
        self.create_publication(title="Published one")
        self.create_publication(title="Published two")
        self.create_publication(title="Draft", status=Publication.Status.DRAFT)

        response = self.client.get(self.homepage.url)

        self.assertContains(response, 'data-statistic="publications">2</span>')

    def test_homepage_statistic_fallbacks(self):
        self.homepage.team_member_count = None
        self.homepage.research_areas = ""
        self.homepage.save_revision().publish()

        response = self.client.get(self.homepage.url)

        self.assertContains(response, "Not listed", count=2)
        self.assertContains(response, 'data-statistic="publications">0</span>')

    def test_publication_is_registered_in_wagtail_admin(self):
        editor = get_user_model().objects.create_superuser(
            username="publication-editor",
            email="publication-editor@example.com",
            password="test-password",
        )
        self.client.force_login(editor)

        response = self.client.get(reverse("wagtailsnippets_home_publication:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Publications")
