"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import environ

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = env.bool('DEBUG', default=False)
SECRET_KEY = env('SECRET_KEY')

DATABASES = {'default': env.db(default='sqlite:///' + (BASE_DIR / 'db.sqlite3').absolute().as_posix()), }
CACHES = {'default': env.cache(default="locmemcache://")}
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])

GOOGLE_OAUTH_CLIENT_ID = env("GOOGLE_OAUTH_CLIENT_ID", default=None)
GOOGLE_HOSTED_DOMAIN = env("GOOGLE_HOSTED_DOMAIN", default=None)

# These are for DigitalOcean Spaces
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default=None)
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default=None)
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default=None)
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default=None)
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default=None)

DEFAULT_FILE_STORAGE = env("DEFAULT_FILE_STORAGE", default="django.core.files.storage.FileSystemStorage")
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False

# Remote logging configuration
LOGZ_REMOTE_URL = env('LOGZ_REMOTE_URL', default=None)
LOGZ_TOKEN = env('LOGZ_TOKEN', default=None)

# Application definition

AUTH_USER_MODEL = 'accounts.User'

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'adminsortable2',
    'django_safemigrate.apps.SafeMigrateConfig',
    'bootstrap4',
    'health_check',
    'health_check.db',
    'django_bootstrap_breadcrumbs',
    'versatileimagefield',
    'rest_framework',
    'solo',

    'accounts',
    'icons',
    'nav',
    'calendar_generator',
    'sis',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    # Inject the debug toolbar
    security_index = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
    MIDDLEWARE.insert(security_index+1, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INSTALLED_APPS.append('debug_toolbar.apps.DebugToolbarConfig')


ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],

        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'accounts.context_processors.has_admin_access'
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_ROOT = BASE_DIR / "scratch" / "media"
MEDIA_URL = env.str("MEDIA_URL", "/media/")

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / "scratch" / "static"
STATICFILES_DIRS = [BASE_DIR / "static"]

INTERNAL_IPS = [
    '127.0.0.1',
    '[::1]',
]

LOGIN_REDIRECT_URL = "/"

RESULTS_CACHE_SIZE = 2500

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'logzioFormat': {},
        'verbose': {
            'format': '%(asctime)s %(name)s [%(levelname)s] %(filename)s:%(lineno)d %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}

if LOGZ_REMOTE_URL and LOGZ_TOKEN:
    LOGGING['handlers']['logzio'] = {
        'class': 'logzio.handler.LogzioHandler',
        'level': 'INFO',
        'formatter': 'logzioFormat',
        'token': 'token',
        'logzio_type': "django",
        'logs_drain_timeout': 5,
        'url': LOGZ_REMOTE_URL,
        'debug': True,
        'network_timeout': 10,
        'token': LOGZ_TOKEN,
    }

    LOGGING['loggers']['django']['handlers'].append('logzio')
