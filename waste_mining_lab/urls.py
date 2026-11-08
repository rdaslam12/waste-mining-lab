from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin
from django.views.static import serve

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views
from home import views as home_views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),
    path("research/<slug:slug>/", home_views.project_detail, name="project_detail"),
    path("publications/<int:pk>/bibtex/", home_views.publication_bibtex, name="publication_bibtex"),
    # Serve media files (e.g. uploaded hero images, publication documents)
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static files from development server
    urlpatterns += staticfiles_urlpatterns()

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
]
