# Waste Mining Lab — pinned photo hero (no migrations)

Files are structured relative to your Django project root (`waste-mining-lab/`). Copy the three files to the same paths in your project.

## 1. Remove the previous Bento Grid references

In `home/templates/home/home_page.html`, remove the line:

```django
{% include "home/includes/featured_grid.html" %}
```

If you added stylesheet/script blocks for `wml-featured.css` and `wml-featured.js`, remove those references. You can leave the old files in the project unused for now.

## 2. Replace only the old image section

In `home/templates/home/home_page.html`, locate the entire existing section starting with:

```html
<section class="research-image" aria-label="Laboratory research image">
```

Delete that section through its matching closing `</section>` (just before `<section class="mission" ...>`). Replace it with:

```django
{% include "home/includes/pinned_hero.html" %}
```

Leave the mission, introduction, team, and rest of the homepage intact.

## 3. Load the new CSS and JS only on the homepage

At the top of `home/templates/home/home_page.html`, use:

```django
{% load static wagtailcore_tags wagtailimages_tags %}
```

Below `{% block body_class %}template-homepage{% endblock %}`, add:

```django
{% block extra_css %}
    {{ block.super }}
    <link rel="stylesheet" href="{% static 'css/wml-pinned-hero.css' %}">
{% endblock %}
```

At the bottom of `home_page.html`, after `{% endblock content %}`, add:

```django
{% block extra_js %}
    {{ block.super }}
    <script src="{% static 'js/wml-pinned-hero.js' %}" defer></script>
{% endblock %}
```

If the old grid already created `extra_css` or `extra_js` blocks, edit their contents rather than creating duplicate blocks.

## 4. Keep the existing section links

The new hero scroll link points to `#research`, which already exists on the current lab introduction section. No changes to that section or its existing links are needed.

## 5. Choose the photograph

Log into Wagtail admin → Pages → Home → Edit → Hero image. Upload and select a high-quality photograph with **no text already baked into the image**, then Publish. The template uses the existing `page.hero_image` field. If no image is selected, it uses the previously created `static/images/lab-header.webp` image.

## 6. Test

- `python manage.py check`
- `python manage.py runserver`
- Open `/` and hard refresh (Cmd+Shift+R).
- Verify one message fades into the next around every seven seconds.
- Scroll past the hero: the mission section should cover the pinned photo from the bottom upward.
- Check mobile viewport and reduced-motion settings.

**Do not edit** `base.html`, `wml-nav.css`, or the existing navbar JavaScript for this feature.

Note: CSS `position: sticky` can fail if any ancestor of the hero gets `overflow: hidden/auto/scroll` or a restrictive height. The provided files do not add those properties to ancestor elements.
