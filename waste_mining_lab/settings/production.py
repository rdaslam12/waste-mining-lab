import os
from .base import *

DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")

# Require or safely fall back for SECRET_KEY
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    os.environ.get("SECRET_KEY", "django-insecure-production-fallback-key-replace-in-env-if-needed-wml"),
)

# Allowed hosts: accept comma-separated list, wildcard onrender, or render external hostname
allowed_hosts_env = os.environ.get("ALLOWED_HOSTS")
if allowed_hosts_env:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(",") if host.strip()]
else:
    ALLOWED_HOSTS = [
        ".onrender.com",
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "*"  # safe fallback for initial deployment
    ]

render_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if render_hostname and render_hostname not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_hostname)

CSRF_TRUSTED_ORIGINS = [
    "https://*.onrender.com",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
render_url = os.environ.get("RENDER_EXTERNAL_URL")
if render_url and render_url not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append(render_url)

# Database persistence:
# If DATABASE_URL is set (e.g. Render PostgreSQL), configure dj_database_url with connection pooling.
# Otherwise, fall back to SQLite in BASE_DIR.
database_url = os.environ.get("DATABASE_URL")
if database_url:
    try:
        import dj_database_url
        DATABASES = {
            "default": dj_database_url.config(
                default=database_url,
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
    except ImportError:
        pass

# Optional persistent media directory (e.g., Render Persistent Disk mount)
media_dir = os.environ.get("MEDIA_DIR")
if media_dir:
    MEDIA_ROOT = media_dir

# Use WhiteNoise to serve static files with compression and caching
STORAGES["staticfiles"]["BACKEND"] = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}

try:
    from .local import *
except ImportError:
    pass
