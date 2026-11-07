# Waste Mining Lab website

The official website foundation for Waste Mining Lab at North South University, Bangladesh. The site uses Django and Wagtail so lab administrators can manage public content through Wagtail's built-in admin.

## Technology

- Python 3.12
- Django 6.1
- Wagtail 8.1
- SQLite for local development

## Local setup

Create and activate a Python 3.12 virtual environment, then install the pinned dependency ranges:

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

The headline appears in the centered title area, the subtitle in the dark mission band, the image as a panoramic banner, and the introduction in the research section. When uploading a hero image, add contextual alt text in Wagtail's image description field; leave it empty only when the image is decorative. Until authentic lab photographs are available, the homepage displays clearly labeled research and portrait placeholders. The team section features only the verified lab director.

The layout follows the provided academic lab reference, while the content and any future photographs must belong to Waste Mining Lab.

The locally hosted DM Sans and Newsreader fonts are distributed under the SIL Open Font License, with license files beside the fonts in `waste_mining_lab/static/fonts/`. The botanical placeholder is original vector artwork and stops animating when reduced motion is requested.

## Checks

```bash
python manage.py check
python manage.py test
```

Production settings live in `waste_mining_lab/settings/production.py`. Configure a production secret key, allowed hosts, database, media storage, and `WAGTAILADMIN_BASE_URL` before deployment.
