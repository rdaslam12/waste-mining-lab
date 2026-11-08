"""Integration checks use synthetic fixtures only in Django's isolated test database."""
import importlib
import tempfile
from datetime import date
from io import BytesIO
from types import SimpleNamespace

from PIL import Image as PILImage
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test import TestCase, override_settings
from django.urls import reverse
from wagtail.images import get_image_model
from wagtail.models import Page, PageViewRestriction, Site

from home.models import (
    Activity, ActivityImage, Grant, HomePage, NewsArticlePage, Publication,
    ResearchArea, ResearchProject, SectionPage, TeamMember,
)
from home.page_context import SECTION_TEMPLATES


class SecondaryPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.home = HomePage.objects.first()
        Site.objects.all().delete()
        Site.objects.create(hostname="localhost", root_page=cls.home, is_default_site=True)
        cls.sections = {page.slug: page for page in SectionPage.objects.child_of(cls.home)}
        cls.editor = get_user_model().objects.create_superuser("secondary-editor", "editor@example.com", "test-password")

    def publication(self, title="Synthetic test publication", **kwargs):
        payload = {
            "authors": "Test fixture author",
            "year": 2026,
            "status": "published",
        }
        payload.update(kwargs)
        return Publication.objects.create(title=title, **payload)

    def project(self, title="Synthetic test project", **kwargs):
        return ResearchProject.objects.create(title=title, summary="Test-only project summary.", **kwargs)

    def activity(self, title="Synthetic test activity", **kwargs):
        return Activity.objects.create(title=title, date=date(2026, 1, 1), category="field", description="<p>Test-only field notes.</p>", **kwargs)

    def article(self, title="Synthetic test story", publish=True, **kwargs):
        article = NewsArticlePage(title=title, date=date(2026, 1, 1), excerpt="Test-only excerpt.", body="<p>Test-only article body.</p>", live=False, **kwargs)
        self.sections["news"].add_child(instance=article)
        revision = article.save_revision()
        if publish:
            revision.publish()
        return article

    def image(self):
        temporary_media = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_media.cleanup)
        settings = override_settings(MEDIA_ROOT=temporary_media.name)
        settings.enable()
        self.addCleanup(settings.disable)
        data = BytesIO()
        PILImage.new("RGB", (120, 90), color="#e2ece1").save(data, format="PNG")
        return get_image_model().objects.create(title="Test image", description="A synthetic test image.", file=SimpleUploadedFile("test.png", data.getvalue(), content_type="image/png"))

    def test_normal_migrations_provide_all_seven_routes(self):
        self.assertEqual(set(self.sections), set(SECTION_TEMPLATES))
        for slug, template in SECTION_TEMPLATES.items():
            with self.subTest(slug=slug):
                response = self.client.get(f"/{slug}/")
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, template)
                self.assertContains(response, "css/wml-sections.css")
                self.assertContains(response, 'id="main-content"')
                for destination in SECTION_TEMPLATES:
                    self.assertContains(response, f'href="/{destination}/"')

    def test_setup_is_idempotent_and_preserves_existing_content(self):
        page = self.sections["research"]
        page.intro = "Existing introduction must remain."
        page.save_revision().publish()
        identifiers = list(Page.objects.values_list("pk", "slug", "path", "url_path"))
        bootstrap = importlib.import_module("home.migrations.0008_ensure_section_pages")
        bootstrap.ensure_sections(apps, SimpleNamespace(connection=connection))
        bootstrap.ensure_sections(apps, SimpleNamespace(connection=connection))
        self.assertEqual(identifiers, list(Page.objects.values_list("pk", "slug", "path", "url_path")))
        page.refresh_from_db()
        self.assertEqual(page.intro, "Existing introduction must remain.")
        self.home.refresh_from_db()
        self.assertEqual(self.home.numchild, self.home.get_children().count())

    def test_setup_adds_only_missing_pages_even_after_deleted_path(self):
        self.sections["team"].delete()
        bootstrap = importlib.import_module("home.migrations.0008_ensure_section_pages")
        bootstrap.ensure_sections(apps, SimpleNamespace(connection=connection))
        self.assertEqual(SectionPage.objects.child_of(self.home).count(), len(self.sections))
        self.assertEqual(self.client.get("/team/").status_code, 200)
        self.assertEqual(Page.find_problems(), ([], [], [], [], []))

    def test_homepage_does_not_load_secondary_styles(self):
        response = self.client.get("/")
        self.assertNotContains(response, "wml-sections.css")
        for asset in ("wml-pinned-hero.js", "wml-mission.js", "wml-faculty.js"):
            self.assertContains(response, asset)

    def test_publications_search_year_and_visibility(self):
        self.publication("Synthetic recovery study", venue="Synthetic venue", abstract="Test-only abstract about metals.", featured=True)
        other = self.publication("Synthetic older study")
        other.year = 2024
        other.save()
        Publication.objects.create(title="Secret draft", authors="Test", year=2026, status="draft", featured=True)
        for query in ("recovery", "metals", "Synthetic venue", "fixture author"):
            response = self.client.get("/publications/", {"q": query, "year": "2026"})
            self.assertContains(response, "Synthetic recovery study")
            self.assertNotContains(response, "Synthetic older study")
            self.assertNotContains(response, "Secret draft")
        self.assertContains(self.client.get("/publications/"), "Publication Index")

    def test_publications_invalid_year_and_empty_search_do_not_error(self):
        self.publication()
        for year in ("banana", "99999999999999999999", "-1", "２０２６", "²"):
            with self.subTest(year=year):
                response = self.client.get("/publications/", {"year": year})
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "No matching publications")
                self.assertContains(response, "Clear filters")
        self.assertContains(self.client.get("/publications/", {"q": "missing"}), "No matching publications")

    def test_publication_abstract_links_and_pagination(self):
        publication = self.publication(doi="10.0000/test-only", publication_url="https://example.com/test", abstract="Test-only abstract")
        doi_pub = self.publication("DOI only work", doi="10.0000/doi-only-test")
        response = self.client.get("/publications/")
        self.assertContains(response, "<summary>Read abstract</summary>", html=True)
        self.assertContains(response, f'id="publication-{publication.pk}"')
        self.assertContains(response, 'href="https://example.com/test"')
        self.assertContains(response, 'href="https://doi.org/10.0000/doi-only-test"')
        for index in range(14):
            self.publication(f"Synthetic numbered test {index}")
        response = self.client.get("/publications/", {"q": "Synthetic", "year": "2026", "page": "2"})
        self.assertContains(response, "Page 2 of 2")
        self.assertContains(response, "q=Synthetic&amp;year=2026&amp;page=1")
        self.assertEqual(self.client.get("/publications/", {"page": "invalid"}).status_code, 200)

    def test_research_uses_homepage_area_fallback_without_modifying_it(self):
        original = self.home.research_areas
        response = self.client.get("/research/")
        for area in self.home.configured_research_areas:
            self.assertContains(response, area)
        self.home.refresh_from_db()
        self.assertEqual(self.home.research_areas, original)

    def test_research_records_and_relationship_visibility(self):
        area = ResearchArea.objects.create(title="Published test area", description="Test-only area description", is_published=True)
        ResearchArea.objects.create(title="Secret area")
        project = self.project("Published test project", area=area, is_published=True, monitoring_related=True, description="<p>Test project details</p>", external_url="https://example.com/project")
        self.project("Secret project")
        public = self.publication("Linked test publication")
        draft = Publication.objects.create(title="Secret publication", authors="Test", year=2026)
        project.publications.add(public, draft)
        project.save()
        response = self.client.get("/research/")
        for value in ("Published test area", "Published test project"):
            self.assertContains(response, value)
        for value in ("Secret area", "Secret project", "Secret publication"):
            self.assertNotContains(response, value)
        response = self.client.get("/waste-monitoring/")
        self.assertNotContains(response, "Connected Research Projects")
        self.assertNotContains(response, "Related Publications")
        self.assertNotContains(response, "Secret publication")

    def test_team_fallback_groups_order_and_related_projects(self):
        response = self.client.get("/team/")
        self.assertContains(response, "Dr. Asef")
        self.assertContains(response, "asef-redwan-1080.webp")
        self.assertNotContains(response, ">Alumni</h2>")
        project = self.project(is_published=True)
        secret = self.project("Secret related project")
        member = TeamMember.objects.create(name="Test student first", role="Test student", category="student", sort_order=1, is_published=True, email="fixture@example.com")
        member.projects.add(project, secret)
        member.save()
        TeamMember.objects.create(name="Test student second", role="Test student", category="student", sort_order=2, is_published=True)
        TeamMember.objects.create(name="Secret member", role="Test researcher")
        response = self.client.get("/team/")
        self.assertContains(response, 'href="mailto:fixture@example.com"')
        self.assertLess(response.content.index(b"Test student first"), response.content.index(b"Test student second"))
        self.assertContains(response, project.title)
        self.assertNotContains(response, "Secret related project")
        self.assertNotContains(response, "Secret member")

    def test_director_can_be_managed_in_cms(self):
        TeamMember.objects.create(name="Dr. Asef M. Redwan", role="Lab director", category="director", biography="Editor-managed director biography.", is_published=True)
        response = self.client.get("/team/")
        self.assertContains(response, "Editor-managed director biography.")
        self.assertNotContains(response, "director-portrait")

    def test_activity_order_gallery_and_published_only(self):
        image = self.image()
        project = self.project(is_published=True)
        old = self.activity("Older test field activity", is_published=True, cover_image=image, project=project)
        ActivityImage.objects.create(activity=old, image=image, caption="Test gallery caption")
        newer = self.activity("Newer test workshop", is_published=True)
        newer.date = date(2026, 2, 1)
        newer.save()
        self.activity("Secret activity", featured=True)
        response = self.client.get("/activity/")
        self.assertContains(response, "Test gallery caption")
        self.assertContains(response, "A synthetic test image.")
        self.assertContains(response, f'/research/#project-{project.pk}')
        self.assertNotContains(response, "Secret activity")
        self.assertLess(response.content.index(b"Newer test workshop"), response.content.index(b"Older test field activity"))

    def test_news_pages_support_drafts_publishing_and_private_pages(self):
        published = self.article("Published test news", featured=True)
        draft = self.article("Secret draft news", publish=False)
        private = self.article("Restricted test news")
        PageViewRestriction.objects.create(page=private, restriction_type="password", password="test")
        response = self.client.get("/news/")
        self.assertContains(response, "Published test news")
        self.assertNotContains(response, "Secret draft news")
        self.assertNotContains(response, "Restricted test news")
        self.assertEqual(self.client.get(draft.url).status_code, 404)
        response = self.client.get(published.url)
        self.assertTemplateUsed(response, "home/pages/news_article.html")
        self.assertContains(response, "Test-only article body.")
        self.assertContains(response, 'href="/news/"')
        self.assertNotContains(response, "Restricted test news")

    def test_activity_links_find_entries_on_later_archive_pages(self):
        oldest = self.activity("Old featured activity", is_published=True, featured=True)
        for index in range(11):
            self.activity(f"Newer activity {index}", is_published=True)
        self.assertEqual(oldest.archive_url, f"/activity/?page=2#activity-{oldest.pk}")
        self.assertContains(self.client.get("/activity/"), oldest.archive_url)
        self.assertContains(self.client.get("/activity/?page=2"), f'id="activity-{oldest.pk}"')

    def test_news_filters_and_related_content(self):
        project = self.project("Public article project", is_published=True)
        secret_activity = self.activity("Secret news activity")
        article = self.article("Research test news", category="research", related_project=project, related_activity=secret_activity)
        self.article("Announcement test news", category="announcement")
        response = self.client.get("/news/", {"category": "research"})
        self.assertContains(response, "Research test news")
        self.assertNotContains(response, "Announcement test news")
        self.assertContains(self.client.get("/news/", {"category": "missing"}), "No news in this category yet")
        response = self.client.get(article.url)
        self.assertContains(response, "Public article project")
        self.assertNotContains(response, "Secret news activity")

    def test_news_can_only_be_created_below_news_index(self):
        self.assertTrue(NewsArticlePage.can_create_at(self.sections["news"]))
        for slug, page in self.sections.items():
            if slug != "news":
                self.assertFalse(NewsArticlePage.can_create_at(page))

    def test_monitoring_is_explicitly_disconnected_and_methodology_editable(self):
        page = self.sections["waste-monitoring"]
        page.methodology = "<p>Editor-provided methodology context.</p>"
        page.save_revision().publish()
        response = self.client.get(page.url)
        for value in ("Data source not connected", "Visualization awaiting verified dataset", "No locations published", "Editor-provided methodology context."):
            self.assertContains(response, value)
        self.assertNotContains(response, "<canvas")
        self.assertNotContains(response, "Live data")

    def test_contact_details_and_email(self):
        response = self.client.get("/contact/")
        for value in ("North South University", "Bashundhara, Dhaka-1229", 'href="mailto:asef.redwan@northsouth.edu"', "google.com/maps/search/"):
            self.assertContains(response, value)

    def test_all_section_editors_and_news_editor_open(self):
        self.client.force_login(self.editor)
        article = self.article()
        for page in [*self.sections.values(), article]:
            with self.subTest(page=page.title):
                response = self.client.get(reverse("wagtailadmin_pages:edit", args=[page.pk]))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'name="body"')

    def test_snippet_editors_and_create_forms_open(self):
        self.client.force_login(self.editor)
        records = [ResearchArea.objects.create(title="Test area"), self.project(), TeamMember.objects.create(name="Test member", role="Test role"), self.activity(), self.publication()]
        for record in records:
            model_name = record._meta.model_name
            with self.subTest(model=model_name):
                for operation in ("list", "add", "edit"):
                    response = self.client.get(reverse(f"wagtailsnippets_home_{model_name}:{operation}", args=[record.pk] if operation == "edit" else []))
                    self.assertEqual(response.status_code, 200)

    def test_page_image_and_editorial_content_are_rendered(self):
        image = self.image()
        page = self.sections["research"]
        page.heading = "An editable heading"
        page.body = "<p>Editor-managed approach</p>"
        page.feature_image = image
        page.image_caption = "Editor-managed caption"
        page.save_revision().publish()
        response = self.client.get(page.url)
        for value in ("An editable heading", "Editor-managed approach", "Editor-managed caption", "A synthetic test image."):
            self.assertContains(response, value)

    def test_grants_section_and_classification_categories(self):
        lab_grant = Grant.objects.create(
            title="Synthetic Lab Grant",
            funding_organization="NSU Research Fund",
            amount_display="BDT 14 Lakh",
            category=Grant.Category.LAB,
            is_published=True,
            is_verified=True,
            end_date=date(2027, 12, 31),
        )
        prev_grant = Grant.objects.create(
            title="Synthetic Previous Grant",
            funding_organization="US DOE",
            amount_display="USD 898,265",
            category=Grant.Category.PREVIOUS,
            is_published=True,
            is_verified=True,
            end_date=date(2022, 9, 30),
        )
        Grant.objects.create(
            title="Secret Draft Grant",
            funding_organization="Draft Corp",
            is_published=False,
        )

        response = self.client.get("/grants/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Synthetic Lab Grant")
        self.assertContains(response, "Active Funding")
        self.assertContains(response, "Synthetic Previous Grant")
        self.assertContains(response, "Previous Funding")
        self.assertNotContains(response, "Secret Draft Grant")

    def test_project_detail_view_and_absolute_url(self):
        project = self.project(
            "Detailed Waste Study",
            slug="detailed-waste-study",
            is_published=True,
            description="<p>Full project description text.</p>",
            methodology="<p>Detailed experimental protocol.</p>",
            funding_notes="Funded by Test Council",
        )
        pub = self.publication("Linked Project Publication")
        project.publications.add(pub)
        project.save()

        response = self.client.get("/research/detailed-waste-study/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Detailed Waste Study")
        self.assertContains(response, "Full project description text.")
        self.assertContains(response, "Detailed experimental protocol.")
        self.assertNotContains(response, "Related Publications")
        self.assertNotContains(response, "Linked Project Publication")

        # Unknown slug returns 404
        response_404 = self.client.get("/research/non-existent-project-slug/")
        self.assertEqual(response_404.status_code, 404)

    def test_publication_type_filtering_and_bibtex_export(self):
        journal_pub = self.publication("Journal Paper A", publication_type=Publication.PublicationType.JOURNAL)
        chapter_pub = self.publication("Book Chapter B", publication_type=Publication.PublicationType.BOOK_CHAPTER)

        # Filter by book chapter
        response = self.client.get("/publications/", {"type": "book_chapter"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Book Chapter B")
        self.assertNotContains(response, "Journal Paper A")

        # BibTeX export
        response_bib = self.client.get(f"/publications/{journal_pub.pk}/bibtex/")
        self.assertEqual(response_bib.status_code, 200)
        self.assertEqual(response_bib["Content-Type"], "text/plain; charset=utf-8")
        self.assertIn("Journal Paper A", response_bib.content.decode("utf-8"))
        self.assertIn("@article{", response_bib.content.decode("utf-8"))

    def test_import_verified_academic_data_command(self):
        from django.core.management import call_command
        # Running command idempotently
        call_command("import_verified_academic_data", dry_run=True)
        call_command("import_verified_academic_data")
        self.assertTrue(Publication.objects.filter(doi="10.1021/acsomega.5c09729").exists())
        self.assertTrue(Grant.objects.filter(category=Grant.Category.LAB).exists())

    def test_global_footer_connect_the_lab_button_and_no_promotional_cta(self):
        for path in ("/", "/publications/", "/research/", "/grants/", "/team/", "/activity/", "/waste-monitoring/", "/news/", "/contact/"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'href="/contact/" class="site-footer__btn">Contact the Lab</a>')
                self.assertNotContains(response, "Research starts with a conversation.")
                self.assertNotContains(response, "Ideas travel further together.")
                self.assertNotContains(response, "Partner with our research.")
                self.assertNotContains(response, "editorial-breadcrumb")

    def test_publications_live_search_ajax_partial(self):
        self.publication("Machine learning waste study", year=2026)
        response = self.client.get("/publications/?q=Machine", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="publication-results"')
        self.assertContains(response, "Machine learning waste study")
        self.assertNotContains(response, "<!doctype html>")

    def test_publication_record_streamlined_layout(self):
        pub = self.publication(
            "Bioreactor dye removal study",
            venue="Bioresource Technology",
            authors="Asef M. Redwan, Jane Doe",
            doi="10.1016/j.biortech.test",
            publication_url="https://example.com/biortech-paper",
            abstract="Study of continuous flow bio-reactors.",
        )
        response = self.client.get("/publications/")
        self.assertContains(response, "Bioresource Technology")
        self.assertContains(response, 'href="https://example.com/biortech-paper"')
        self.assertContains(response, "Asef M. Redwan, Jane Doe")
        self.assertContains(response, "<summary>Read abstract</summary>", html=True)
        self.assertContains(response, "Cite / BibTeX")
        self.assertNotContains(response, "pub-type-badge")
        self.assertNotContains(response, "View publication")

    def test_research_page_only_active_projects_and_no_extra_sections(self):
        area = ResearchArea.objects.create(title="Resource recovery", is_published=True)
        active_proj = self.project("Active Biomass Reactor", area=area, status="active", is_published=True)
        completed_proj = self.project("Completed Older Study", area=area, status="completed", is_published=True)
        response = self.client.get("/research/")
        self.assertContains(response, "Our Research Areas")
        self.assertContains(response, "Research in Focus")
        self.assertContains(response, "Active Biomass Reactor")
        self.assertNotContains(response, "Completed Older Study")
        self.assertNotContains(response, "From questions to understanding")
        self.assertNotContains(response, "Further reading")

    def test_team_page_structure_and_alumni_toggle(self):
        TeamMember.objects.create(name="Current Assistant One", role="Research Assistant", category="assistant", is_published=True, scholar_url="https://scholar.google.com/test")
        TeamMember.objects.create(name="Scientist Contributor", role="Research Scientist", category="scientist", is_published=True)
        TeamMember.objects.create(name="Former Member Alum", role="Former RA", category="alumni", is_published=True, alumni_current_position="PhD Student, Stanford")
        response = self.client.get("/team/")
        self.assertContains(response, "team-photo.png")
        self.assertContains(response, "Laboratory Leadership")
        self.assertContains(response, "Research Assistants")
        self.assertContains(response, "Current Assistant One")
        self.assertContains(response, "Other Contributors")
        self.assertContains(response, "Scientist Contributor")
        self.assertContains(response, "Show Alumni")
        self.assertContains(response, "Former Member Alum")
