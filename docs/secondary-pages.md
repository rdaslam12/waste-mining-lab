# Secondary pages: maintainer guide

The seven sections extend the established Django/Wagtail site. The homepage, shared header, and footer retain their existing presentation. New content is managed through Wagtail at `/admin/`; empty states remain until verified records are published.

## Start locally

From the project root, use the existing environment:

```bash
source .venv/bin/activate
python manage.py migrate
python manage.py runserver
```

For first-time installation and admin account creation, follow [README.md](../README.md#local-setup). The public site is at `http://127.0.0.1:8000/` and Wagtail is at `http://127.0.0.1:8000/admin/`.

Migration `0007` adds section fields and editorial models. Migration `0008` creates only missing section destinations under each Home page. It is idempotent and preserves existing page content, slugs, IDs, and types. Its reverse operation deliberately retains pages, including subsequent editorial changes. Neither migration seeds fictional lab records.

## Edit section pages

In **Pages → Home**, edit the existing section and publish the changes. Keep the following slugs: they select both the page template and its content queries, and existing navigation links use these paths.

| Page | Public path | Main content source |
| --- | --- | --- |
| Publications | `/publications/` | Publication snippets |
| Research | `/research/` | Research areas and research projects |
| Team | `/team/` | Team members and the established director fallback |
| Activity | `/activity/` | Activity snippets and their inline galleries |
| News | `/news/` | Published News article pages beneath News |
| Waste Monitoring | `/waste-monitoring/` | Editorial methods and monitoring-related projects |
| Contact | `/contact/` | Established contact details and editable supporting copy |

Each section has an optional **Heading** for its display title, **Intro**, and **Body**. Changing Heading does not change the navigation title. Body supplies supporting prose; on Research it describes the research approach, on Waste Monitoring it supplies the overview, and on Contact it replaces the collaboration/inquiry guidance. Use Wagtail's Promote fields for search descriptions.

**Feature image** and **Image caption** are displayed by Research, Activity, Waste Monitoring, and Contact. **Methodology** supplies the Waste Monitoring “Methods & context” section. Although these fields share one admin form, only their relevant templates display them.

Contact uses the existing director email and university address, with email and university-location links. Those fixed details live in `home/templates/home/pages/contact.html`; there is no contact form or mail-delivery backend.

## Publish verified records

Open **Snippets** in Wagtail to manage Publications, Research areas, Research projects, Team members, and Activities. New research, team, and activity records default to **Is published = false**. Save verified content with that box selected to make it public; clear it to hide the record. These are snippet visibility flags, separate from the Wagtail page publishing workflow.

- **Publications:** the established model retains its Draft/Published **Status**. Add title, authors in publication order, year, journal/conference, optional DOI, URL, and abstract. DOI values are unique when supplied. Featured records can appear in Selected work. The archive searches title, authors, venue, abstract, and DOI; combines search with a year filter; and paginates 12 records at a time. Abstracts use native keyboard-accessible disclosure controls.
- **Research areas:** add a title, description, optional image, and sort order. If none are published, Research uses the parent Home page's configured research-area labels. Publishing areas replaces that fallback on Research; it does not change the homepage's configured labels.
- **Research projects:** add summary, optional image, detailed description, research area, publications, and external URL. Select **Monitoring related** to also show a published project on Waste Monitoring. Related publication links display only published publications.
- **Team members:** choose director, researcher, student, collaborator, or alumni; add role, affiliation, biography, research interests, optional photograph/contact/profile links, and related projects. Published directors replace the established director fallback on Team only. Without a published director record, the existing Dr. Asef M. Redwan profile and portrait remain visible. Other groups appear only when populated, and related project links require published projects. Sort order controls directory ordering.
- **Activities:** supply date, category, description, optional cover photograph, project, and external link. Use **Gallery photograph** rows to add and reorder images with optional captions. Gallery thumbnails open the original image; the full gallery appears in the journal entry. The archive orders newest first and paginates 10 entries at a time. Featured selects a highlighted entry; links to older entries include the correct archive page.

Publishing a relationship does not automatically publish its target. Verify the linked record's visibility separately. Research-area and project ordering uses sort order, then record ID.

For editorial photographs, provide useful text in the Wagtail image **Description** field. Templates use that description as alternative text, falling back to the image title. Captions provide visible context and do not replace alternative text. Use authentic, authorized imagery and omit images when none are available.

## News workflow

Under **Pages → Home → News**, choose **Add child page → News article page**. Articles can exist only beneath the section whose slug is `news`. Set title, date, category, excerpt, body, and optional cover image, featured flag, and related project/publication/activity.

Save a draft to prepare an article, preview it, then publish using Wagtail's normal controls. The archive and related-story list include only live, public articles; Wagtail privacy restrictions still apply. News has category filtering and 12 articles per archive page. Article pages have their own URLs, full text, and links to published related content.

## Monitoring scope

The portal deliberately reports **Data source not connected**. It has spaces for locations, observations over time, dataset information, summaries, and categories, but displays no invented charts, counts, live readings, locations, or trends. Methodology and related research are editorial content, not a data connection.

Connecting datasets, ingestion, storage, map layers, and chart rendering requires a future implementation. Add verified collection methods, units, equipment, coverage, and limitations through Methodology when available.

## Implementation and visual continuity

`home/models.py` retains `HomePage`, `Publication`, and `SectionPage`; the new editorial models live in `home/content_models.py`. `home/page_context.py` selects content by section slug and handles filtering, publication visibility, and pagination. Templates are in `home/templates/home/pages/`, with reusable fragments in `home/templates/home/includes/`. Unknown section slugs retain the generic section-page fallback.

`home/pages/base_section.html` extends the shared base template and loads `waste_mining_lab/static/css/wml-sections.css`. Keep new section styles scoped to `.wml-editorial`. They inherit the incumbent forest/sage/paper colors and locally hosted DM Sans/Newsreader fonts from the global stylesheet. Each section has its own editorial composition: publication index, research portfolio, people directory, dated journal, news archive, monitoring workspace, and contact layout. Responsive stacking, visible focus, native forms/disclosures, and subtle link interactions carry through without a new global visual system.

`DESIGN.md` and `PRODUCT.md` contain older homepage-only scope and placeholder descriptions. They were preserved during this extension. For the completed secondary pages, the current user brief and active implementation take precedence over those historical descriptions; do not restore obsolete restrictions or placeholders from them.

## Validation

The implementation passed:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
git diff --check
```

Results: no system-check issues, no unrecorded model changes, all 38 Django tests passing, and no diff whitespace errors. Browser review covered all seven empty-state routes at 320, 375, 390, 430, 768, 1024, and 1440 pixels (49 route/width checks), plus 14 populated desktop/mobile route checks. Publication search, year filtering, reset, pagination, keyboard abstracts, news filters/details, mobile navigation, the shared header, and homepage hero rotation, mission canvas, and portrait were checked. No overflow, JavaScript errors, broken image assets, or page/asset HTTP errors were detected in that review; the pre-existing missing favicon was excluded.

Local evidence is under `.impeccable/review/secondary/`, including `review.md`, JSON reports, and screenshots. Captures named `populated-*` use explicitly labelled synthetic fixtures in an isolated `/private/tmp` database. Those fixtures are not real lab content and were not added to the normal development database. External destination availability and formal accessibility certification were not tested.
