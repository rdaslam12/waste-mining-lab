"""Create Grants & Funding navigation destination; never convert or replace pages."""
from django.db import migrations
from django.db.models import F


def ensure_grants_section(apps, schema_editor):
    alias = schema_editor.connection.alias
    Page = apps.get_model("wagtailcore", "Page")
    HomePage = apps.get_model("home", "HomePage")
    SectionPage = apps.get_model("home", "SectionPage")
    ContentType = apps.get_model("contenttypes", "ContentType")
    content_type, _ = ContentType.objects.using(alias).get_or_create(app_label="home", model="sectionpage")
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    grants_info = (
        "grants",
        "Grants & Funding",
        "Sponsored research, competitive grants, and institutional funding supporting environmental engineering and resource recovery research at Waste Mining Lab.",
    )

    for home in HomePage.objects.using(alias).all():
        children = Page.objects.using(alias).filter(path__startswith=home.path, depth=home.depth + 1)
        existing_slugs = set(children.values_list("slug", flat=True))
        if grants_info[0] in existing_slugs:
            continue

        last_path = children.order_by("path").values_list("path", flat=True).last()
        position = int(last_path[-4:], 36) if last_path else 0
        position += 1
        number, suffix = position, ""
        while number:
            number, remainder = divmod(number, 36)
            suffix = alphabet[remainder] + suffix
        if len(suffix) > 4:
            raise RuntimeError("No free child path available for navigation pages.")

        slug, title, intro = grants_info
        SectionPage.objects.using(alias).create(
            title=title, draft_title=title, slug=slug,
            content_type_id=content_type.pk, locale_id=home.locale_id,
            path=home.path + suffix.zfill(4), depth=home.depth + 1,
            numchild=0, url_path=home.url_path + slug + "/",
            live=True, has_unpublished_changes=False,
            intro=intro, search_description=intro,
        )
        Page.objects.using(alias).filter(pk=home.pk).update(numchild=F("numchild") + 1)


class Migration(migrations.Migration):
    dependencies = [("home", "0009_publication_publication_type_and_more")]
    operations = [migrations.RunPython(ensure_grants_section, migrations.RunPython.noop)]
