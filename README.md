# Waste Mining Lab website

The official website for Waste Mining Lab at North South University, Bangladesh. Django and Wagtail provide the public site and editorial admin. Alongside the established homepage, the site includes Publications, Research, Team, Activity, News, Waste Monitoring, and Contact.

## Technology

- Python 3.12
- Django 6.1
- Wagtail 8.1
- SQLite for local development

## Local setup

Activate the existing virtual environment with `source .venv/bin/activate`. For a fresh checkout, create a Python 3.12 environment and install the dependency ranges in `requirements.txt`:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Prepare the database and start the development server:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the public site and `http://127.0.0.1:8000/admin/` for Wagtail. Existing authentication is provided by Django and Wagtail; the project does not implement a separate login system.

## Homepage content

In Wagtail, edit the Home page to manage:

- Hero headline
- Hero subtitle
- Hero image
- Lab introduction
- Optional verified team member count
- Research areas, one per line

The homepage retains its established hero rotation, mission animation, research showcase, and director portrait. Add meaningful descriptions to editorial images in Wagtail. The optional team count must be verified; it is not calculated from the new Team directory.

The secondary pages reuse the existing forest, sage, and paper palette with DM Sans and Newsreader. Their CSS is scoped separately; the homepage, header, and footer remain the shared visual reference.

The locally hosted fonts are distributed under the SIL Open Font License, with license files beside the fonts in `waste_mining_lab/static/fonts/`.

## Secondary pages and editing

See [the secondary-page maintainer guide](docs/secondary-pages.md) for CMS editing routes, publication visibility, project and people relationships, activity galleries, news publishing, and implementation details.

Run `python manage.py migrate` to add the editorial models and any missing section pages. Existing pages, content, slugs, and IDs are preserved. No sample publications, projects, people, activities, or news are inserted. Waste Monitoring intentionally shows that no data source is connected; an ingestion backend is not included.

## Checks

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
git diff --check
```

The secondary-page implementation passed these checks, including 38 Django tests, plus responsive browser checks for empty and populated content. [Validation details](docs/secondary-pages.md#validation) distinguish local fixture captures from real editorial content.

Production settings live in `waste_mining_lab/settings/production.py`. Configure a production secret key, allowed hosts, database, media storage, and `WAGTAILADMIN_BASE_URL` before deployment.
