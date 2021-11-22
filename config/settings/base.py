"""
Base settings to build other settings files upon.
"""
import io
import os
from pathlib import Path

import environ
from google.cloud import secretmanager

ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
APPS_DIR = ROOT_DIR / "fahari"
ENV_PATH = "/tmp/secrets/.env"

env = environ.Env()
env.read_env(ENV_PATH)

if os.environ.get("GOOGLE_CLOUD_PROJECT", None):
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    client = secretmanager.SecretManagerServiceClient()
    settings_name = os.environ.get("SETTINGS_NAME", "mle_django_settings")
    name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
    payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")
    env.read_env(io.StringIO(payload))
    print("set env from secrets...")

# GENERAL
# ------------------------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", False)
TIME_ZONE = "Africa/Nairobi"
LANGUAGE_CODE = "en-us"
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = [str(ROOT_DIR / "locale")]

# DATABASES
# ------------------------------------------------------------------------------
DATABASES = {
    "default": {
        "NAME": env.str("POSTGRES_DB"),
        "USER": env.str("POSTGRES_USER"),
        "PASSWORD": env.str("POSTGRES_PASSWORD"),
        "HOST": env.str("POSTGRES_HOST"),
        "PORT": env.str("POSTGRES_PORT", None),
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "ATOMIC_REQUESTS": True,
    },
}

# URLS
# ------------------------------------------------------------------------------
ROOT_URLCONF = "config.urls"
ASGI_APPLICATION = "config.asgi.application"
WSGI_APPLICATION = "config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.forms",
    "django.contrib.gis",
    "django.contrib.postgres",
]
THIRD_PARTY_APPS = [
    "channels",
    "crispy_forms",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "django_filters",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_datatables",
    "corsheaders",
    "mjml",
    "jet",
    "django.contrib.admin",  # needs to come after jet so that jet static files are preferred
]

LOCAL_APPS = [
    "fahari.users.apps.UsersConfig",
    "fahari.common.apps.CommonConfig",
    "fahari.ops.apps.OpsConfig",
    "fahari.mle.apps.MLEConfig",
    "fahari.misc.apps.MiscConfig",
    "fahari.sims.apps.SimsConfig",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIGRATIONS
# ------------------------------------------------------------------------------
MIGRATION_MODULES = {"sites": "fahari.contrib.sites.migrations"}

# AUTHENTICATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
AUTH_USER_MODEL = "users.User"
LOGIN_REDIRECT_URL = "users:redirect"
LOGIN_URL = "account_login"

# PASSWORDS
# ------------------------------------------------------------------------------
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.common.BrokenLinkEmailsMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# STATIC
# ------------------------------------------------------------------------------
STATIC_ROOT = str(ROOT_DIR / "staticfiles")
STATIC_URL = "/static/"
STATICFILES_DIRS = [str(APPS_DIR / "static")]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
MEDIA_ROOT = str(APPS_DIR / "media")
MEDIA_URL = "/media/"

# TEMPLATES
# ------------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR / "templates")],
        "OPTIONS": {
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "fahari.utils.context_processors.settings_context",
            ],
        },
    }
]
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"
CRISPY_TEMPLATE_PACK = "bootstrap4"
CRISPY_FAIL_SILENTLY = not DEBUG

# FIXTURES
# ------------------------------------------------------------------------------
FIXTURE_DIRS = (str(APPS_DIR / "fixtures"),)

# SECURITY
# ------------------------------------------------------------------------------
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "SAMEORIGIN"  # needs to be SAMEORIGIN for the jet admin to work

# EMAIL
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND",
    default="anymail.backends.mailgun.EmailBackend",
)
DEFAULT_FROM_EMAIL = env(
    "DJANGO_DEFAULT_FROM_EMAIL",
    default="Fahari System <mle@savannahghi.org>",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = env(
    "DJANGO_EMAIL_SUBJECT_PREFIX",
    default="[Fahari System ]",
)
ANYMAIL = {
    "MAILGUN_API_KEY": env("MAILGUN_API_KEY", default=""),  # blank default for local dev and tests
    "MAILGUN_SENDER_DOMAIN": env("MAILGUN_DOMAIN", default="mle.savannahghi.org"),
    "MAILGUN_API_URL": env("MAILGUN_API_URL", default="https://api.mailgun.net/v3"),
}
EMAIL_TIMEOUT = 5

# ADMIN
# ------------------------------------------------------------------------------
ADMIN_URL = "admin/"
ADMINS = [
    (
        "Savannah Informatics Global Health Institute",
        "info@savannahghi.org",
    ),
    (
        "Savannah Informatics Support Team",
        "feedback@healthcloud.co.ke",
    ),
]
MANAGERS = ADMINS

# LOGGING
# ------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s " "%(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}

# django-allauth
# ------------------------------------------------------------------------------
ACCOUNT_ALLOW_REGISTRATION = env.bool("DJANGO_ACCOUNT_ALLOW_REGISTRATION", True)
ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_ADAPTER = "fahari.users.adapters.AccountAdapter"
SOCIALACCOUNT_ADAPTER = "fahari.users.adapters.SocialAccountAdapter"
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
ACCOUNT_SESSION_REMEMBER = None  # ask the user 'Remember me'
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_MIN_LENGTH = 5
SOCIALACCOUNT_AUTO_SIGNUP = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

# django-compressor
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["compressor"]
STATICFILES_FINDERS += ["compressor.finders.CompressorFinder"]
# django-rest-framework
# -------------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_MODEL_SERIALIZER_CLASS": ("rest_framework.serializers.ModelSerializer",),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework_datatables.renderers.DatatablesRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
        "rest_framework.renderers.AdminRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FileUploadParser",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework_datatables.filters.DatatablesFilterBackend",
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "fahari.common.filters.OrganisationFilterBackend",
        "fahari.common.filters.AllottedFacilitiesFilterBackend",
    ),
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework_datatables.pagination.DatatablesPageNumberPagination"
    ),
    "PAGE_SIZE": 100,
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.DjangoModelPermissions",),
    "DEFAULT_METADATA_CLASS": "rest_framework.metadata.SimpleMetadata",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"user": "1000/second", "anon": "1000/minute"},
    "DATETIME_FORMAT": "iso-8601",
    "DATE_FORMAT": "iso-8601",
    "TIME_FORMAT": "iso-8601",
}

CORS_URLS_REGEX = r"^/api/.*$"

# Project specific settings
# ------------------------------------------------------------------------------
# these are used by the base model classes for validation
DECIMAL_PLACES = 4
MAX_IMAGE_HEIGHT = 4320
MAX_IMAGE_WIDTH = 7680
ORGANISATION_NAME = env(
    "ORGANISATION_NAME", default="Savannah Informatics Global Health Institute"
)
ORGANISATION_EMAIL = env("ORGANISATION_EMAIL", default="info@savannahghi.org")
ORGANISATION_PHONE = env("ORGANISATION_PHONE", default="+254790360360")

# used by the user model to assign a default organisation to a user during creation
DEFAULT_ORG_ID = env("DEFAULT_ORG_ID", default="4181df12-ca96-4f28-b78b-8e8ad88b25df")

# BigAutoField needs migration of existing data and either changes to
# dependencies or overriding dependencies
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# mjml responsive emails
MJML_BACKEND_MODE = "cmd"
MJML_EXEC_CMD = "mjml"
MJML_CHECK_CMD_ON_STARTUP = True
WHITELISTED_DOMAINS = env.list(
    "WHITELISTED_DOMAINS",
    default=[
        "savannahghi.org",
    ],
)


SIMS = {"CONSTRAINT_CHECKERS": {"max_value": [], "min_value": []}}
