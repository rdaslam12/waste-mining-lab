import os
import warnings
from .base import *

DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")

# Require or safely configure SECRET_KEY
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-dev-fallback-key-only-for-local-debugging"
    else:
        warnings.warn(
            "DJANGO_SECRET_KEY is not set in environment. Set DJANGO_SECRET_KEY in production.",
            RuntimeWarning,
        )
        SECRET_KEY = "wml-prod-unconfigured-secret-key-please-set-django-secret-key-environment-variable"

# Allowed hosts: accept comma-separated list, wildcard onrender, or render external hostname
allowed_hosts_env = os.environ.get("ALLOWED_HOSTS")
if allowed_hosts_env:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(",") if host.strip()]
else:
    ALLOWED_HOSTS = [
        "waste-mining-lab.onrender.com",
        ".onrender.com",
        "localhost",
        "127.0.0.1",
    ]

render_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if render_hostname and render_hostname not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_hostname)

CSRF_TRUSTED_ORIGINS = [
    "https://*.onrender.com",
    "https://waste-mining-lab.onrender.com",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
render_url = os.environ.get("RENDER_EXTERNAL_URL")
if render_url and render_url not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append(render_url)

csrf_origins_env = os.environ.get("CSRF_TRUSTED_ORIGINS")
if csrf_origins_env:
    for origin in csrf_origins_env.split(","):
        origin = origin.strip()
        if origin and origin not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(origin)

# Base URL for Wagtail notifications and emails
WAGTAILADMIN_BASE_URL = os.environ.get("WAGTAILADMIN_BASE_URL", "https://waste-mining-lab.onrender.com")

# Production Security Headers
if not DEBUG:
    # Render terminates TLS at the proxy and forwards X-Forwarded-Proto: https
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "True").lower() in ("true", "1", "yes")
    CSRF_COOKIE_SECURE = os.environ.get("CSRF_COOKIE_SECURE", "True").lower() in ("true", "1", "yes")
    SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "True").lower() in ("true", "1", "yes")
    SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

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

# Email backend: In Django 6.1+, use MAILERS.
if os.environ.get("EMAIL_HOST"):
    MAILERS = {
        "default": {
            "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
            "OPTIONS": {
                "host": os.environ.get("EMAIL_HOST"),
                "port": int(os.environ.get("EMAIL_PORT", "587")),
                "username": os.environ.get("EMAIL_HOST_USER", ""),
                "password": os.environ.get("EMAIL_HOST_PASSWORD", ""),
                "use_tls": os.environ.get("EMAIL_USE_TLS", "True").lower() in ("true", "1", "yes"),
            },
        },
    }
else:
    # If external email service is not configured, silence mail.E001 deployment check
    MAILERS = {
        "default": {
            "BACKEND": "django.core.mail.backends.dummy.EmailBackend",
        },
    }
    SILENCED_SYSTEM_CHECKS = ["mail.E001"]

try:
    from .local import *
except ImportError:
    pass
