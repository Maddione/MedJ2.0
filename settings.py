import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


def env(name: str, default: str | None = None) -> str:
    """Взима задължителна променлива или вдига ImproperlyConfigured."""
    value = os.getenv(name, default)
    if value is None:
        raise ImproperlyConfigured(f"Environment variable {name} is required.")
    return value


# ───── Security ──────────────────────────────────────────────────────────────
SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

# ───── Applications ─────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Core Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Local
    "MedJ.apps.MedjConfig",
]

# OCR-app (опционален)
if os.getenv("ENABLE_OCRAPI", "false").lower() in ("1", "true"):
    INSTALLED_APPS.append("ocrapi.apps.OcrapiConfig")

# Tailwind (опционален)
if os.getenv("ENABLE_TAILWIND", "false").lower() in ("1", "true"):
    INSTALLED_APPS += ["tailwind", "theme"]
    TAILWIND_APP_NAME = "theme"

# ───── Middleware ───────────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "MedJ2.urls"
WSGI_APPLICATION = "MedJ2.wsgi.application"

# ───── Templates ────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "basetemplates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
    },
]

# ───── Database (SQLite default, env-driven override) ───────────────────────
DB_ENGINE = os.getenv("DB_ENGINE", "sqlite")

if DB_ENGINE == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / os.getenv("SQLITE_NAME", "db.sqlite3"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": env("DB_NAME"),
            "USER": env("DB_USER"),
            "PASSWORD": env("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", ""),
        }
    }

# ───── Password validators ──────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ───── I18N / L10N ──────────────────────────────────────────────────────────
LANGUAGE_CODE = "bg"
LANGUAGES = [("bg", "Bulgarian"), ("en-us", "English (US)")]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Europe/Sofia"
USE_I18N = True
USE_TZ = True

# ───── Static & Media ───────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ───── Other ────────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
OPENAI_API_KEY = env("OPENAI_API_KEY", "")
LOGIN_REDIRECT_URL = "dashboard"
