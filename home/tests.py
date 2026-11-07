from home.models import HomePage

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
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
