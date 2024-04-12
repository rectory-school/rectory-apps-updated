"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from typing import Dict

from pathlib import Path
from email.utils import parseaddr
from secrets import token_hex

import environ

import structlog

try:
    import django_stubs_ext

    django_stubs_ext.monkeypatch()  # This is for nicer typing
except ImportError:
    ...

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent

if (dotenv := (BASE_DIR / ".env")).exists():
    environ.Env.read_env(dotenv)


DEBUG = env.bool("DEBUG", default=False)
SECRET_KEY = env("SECRET_KEY", default=token_hex(64))

DATABASES = {
    "default": env.db(
        default="sqlite:///" + (BASE_DIR / "db.sqlite3").absolute().as_posix()
    ),
}
CACHES = {"default": env.cache(default="locmemcache://")}
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS", default=["http://localhost:8000", "http://127.0.0.1:8000"]
)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=False)
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=False)
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=None)


GOOGLE_OAUTH_CLIENT_ID = env("GOOGLE_OAUTH_CLIENT_ID", default=None)
GOOGLE_HOSTED_DOMAINS = env.list("GOOGLE_HOSTED_DOMAINS", default=[])

# The base URL to use when sending emails
EMAIL_BASE_URL = env("EMAIL_BASE_URL", default="http://localhost")
STORED_MAIL_SEND_ENABLED = env.bool("STORED_MAIL_SEND_ENABLED", default=True)

# These are allowed to be empty so that PR checks can run
BLACKBAUD_TOKEN_URL = env("BLACKBAUD_TOKEN_URL", default=None)
BLACKBAUD_API_BASE = env("BLACKBAUD_API_BASE", default=None)
BLACKBAUD_OAUTH_KEY = env("BLACKBAUD_OAUTH_KEY", default=None)
BLACKBAUD_OAUTH_SECRET = env("BLACKBAUD_OAUTH_SECRET", default=None)

SIS_SYNC_INTERVAL = env.int("SIS_SYNC_INTERVAL", default=3600)

STORAGES = {
    "default": {
        "BACKEND": env(
            "DEFAULT_FILE_STORAGE",
            default="django.core.files.storage.FileSystemStorage",
        )
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

# Mail configuration
MAILGUN_API_KEY = env("MAILGUN_API_KEY", default=None)
MAILGUN_SENDER_DOMAIN = env("MAILGUN_SENDER_DOMAIN", default=None)
SERVER_EMAIL = env("SERVER_EMAIL", default="root@localhost")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="root@localhost")
HOSTED_ENVIRONMENT = env.bool("HOSTED_ENVIRONMENT", False)

ADMINS = tuple(parseaddr(email) for email in env.list("DJANGO_ADMINS", default=[]))
MANAGERS = tuple(parseaddr(email) for email in env.list("DJANGO_MANAGERS", default=[]))

EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.filebased.EmailBackend",
)

EMAIL_FILE_PATH = BASE_DIR / "scratch" / "emails"

if MAILGUN_API_KEY and MAILGUN_SENDER_DOMAIN:
    ANYMAIL = {
        "MAILGUN_API_KEY": MAILGUN_API_KEY,
        "MAILGUN_SENDER_DOMAIN": MAILGUN_SENDER_DOMAIN,
    }

if HOSTED_ENVIRONMENT:
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Application definition

AUTH_USER_MODEL = "accounts.User"

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

# The direct to config settings are to bypass the
# default_app_config RemovedInDjango41Warning warnings
INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "adminsortable2",
    "django_safemigrate",
    "bootstrap4",
    "django_bootstrap_breadcrumbs",
    "solo",
    "job_runner",
    "simple_history",
    "hijack",
    "hijack.contrib.admin",
    "django_node_assets",
]

LOCAL_APPS = [
    "accounts",
    "nav",
    "calendar_generator",
    "stored_mail",
    "blackbaud",
    "enrichment",
]

INSTALLED_APPS += LOCAL_APPS

MIDDLEWARE = [
    "lb_health_check.middleware.AliveCheck",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "hijack.middleware.HijackUserMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "blackbaud.middleware.AcademicRequestMiddleware",
]

if DEBUG:
    # Inject the debug toolbar
    security_index = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
    MIDDLEWARE.insert(
        security_index + 1, "debug_toolbar.middleware.DebugToolbarMiddleware"
    )
    INSTALLED_APPS.append("debug_toolbar.apps.DebugToolbarConfig")


ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "accounts.context_processors.account_processors",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "US/Eastern"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_ROOT = BASE_DIR / "scratch" / "media"
MEDIA_URL = env.str("MEDIA_URL", "/media/")

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "core.node_module_finder.NodeModulesFinder",
]

STATIC_ROOT = BASE_DIR / "scratch" / "static"
STATICFILES_DIRS = [BASE_DIR / "static"]

INTERNAL_IPS = [
    "127.0.0.1",
    "[::1]",
]

LOGIN_REDIRECT_URL = "/"

RESULTS_CACHE_SIZE = 2500

ALIVENESS_URL = "/aliveness_check"

LOGGING: Dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
        "plain_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),
        },
        "key_value": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.KeyValueRenderer(
                key_order=["timestamp", "level", "event", "logger"]
            ),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "plain_console",
        }
    },
    "loggers": {
        "root": {
            "handlers": ["console"],
            "level": "WARNING",
        },
    },
}

for app_name in LOCAL_APPS:
    thing = LOGGING["loggers"]
    LOGGING["loggers"][app_name] = {
        "handlers": ["console"],
        "level": "INFO",
        "propagate": False,
    }

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

NODE_PACKAGE_JSON = BASE_DIR / "package.json"
NODE_MODULES_ROOT = BASE_DIR / "node_modules"
