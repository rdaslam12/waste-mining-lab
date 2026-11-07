"""Create only missing navigation destinations; never convert or replace pages."""
from django.db import migrations
from django.db.models import F


SECTIONS = (
    ("publications", "Publications", "An evolving record of research, ideas and evidence. Explore the work that informs our understanding of waste and its possibilities."),
    ("research", "Research", "Waste is a starting point for questions about materials, resources and the systems that connect them."),
    ("team", "Team", "Meet the people exploring the connections between waste, resources and a more sustainable environment."),
    ("activity", "Activity", "A journal of the lab’s work: observations from the field, exchanges of ideas and moments of discovery."),
    ("waste-monitoring", "Waste Monitoring", "A clearer view of waste begins with careful observation. Explore the role of environmental monitoring in understanding materials, places and change over time."),
    ("news", "News", "Announcements, research updates and news from Waste Mining Lab."),
    ("contact", "Contact", "For academic correspondence, research discussions and general inquiries, get in touch with the lab."),
)


def ensure_sections(apps, schema_editor):
    """Use historical models and Wagtail's four-character materialized tree paths."""
    alias = schema_editor.connection.alias
    Page = apps.get_model("wagtailcore", "Page")
    HomePage = apps.get_model("home", "HomePage")
    SectionPage = apps.get_model("home", "SectionPage")
    ContentType = apps.get_model("contenttypes", "ContentType")
    content_type, _ = ContentType.objects.using(alias).get_or_create(app_label="home", model="sectionpage")
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    for home in HomePage.objects.using(alias).all():
        children = Page.objects.using(alias).filter(path__startswith=home.path, depth=home.depth + 1)
        existing_slugs = set(children.values_list("slug", flat=True))
        last_path = children.order_by("path").values_list("path", flat=True).last()
        position = int(last_path[-4:], 36) if last_path else 0
        added = 0
        for slug, title, intro in SECTIONS:
            if slug in existing_slugs:
                continue
            position += 1
            number, suffix = position, ""
            while number:
                number, remainder = divmod(number, 36)
                suffix = alphabet[remainder] + suffix
            if len(suffix) > 4:
                raise RuntimeError("No free child path available for navigation pages.")
            SectionPage.objects.using(alias).create(
                title=title, draft_title=title, slug=slug,
                content_type_id=content_type.pk, locale_id=home.locale_id,
                path=home.path + suffix.zfill(4), depth=home.depth + 1,
                numchild=0, url_path=home.url_path + slug + "/",
                live=True, has_unpublished_changes=False,
                intro=intro, search_description=intro,
            )
            added += 1
        if added:
            Page.objects.using(alias).filter(pk=home.pk).update(numchild=F("numchild") + added)


class Migration(migrations.Migration):
    dependencies = [("home", "0007_sectionpage_body_sectionpage_feature_image_and_more")]
    # Reversal deliberately retains editorial pages and any content added to them.
    operations = [migrations.RunPython(ensure_sections, migrations.RunPython.noop)]
