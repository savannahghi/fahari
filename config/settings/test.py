"""
With these settings, tests run faster.
"""
import sys

from model_bakery import baker

from .base import *  # noqa
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="Rk17fN36z2vK71ML7rB4IRvZ0eEDPhdXpOmEYEMk5NmQls4QNhkcjMPjyTQrX3O5",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#test-runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# TEMPLATES
# ------------------------------------------------------------------------------
TEMPLATES[-1]["OPTIONS"]["loaders"] = [  # type: ignore[index] # noqa F405
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Your stuff...
# ------------------------------------------------------------------------------


def gen_func():
    return "+254790360360"


baker.generators.add("phonenumber_field.modelfields.PhoneNumberField", gen_func)

# test with the real storages

# STORAGES
# ------------------------------------------------------------------------------
# https://django-storages.readthedocs.io/en/latest/#installation
INSTALLED_APPS += ["storages", "channels"]  # noqa F405
GS_BUCKET_NAME = env("DJANGO_GCP_STORAGE_BUCKET_NAME", default="fahari-ya-jamii-test")
GS_DEFAULT_ACL = "project-private"
# STATIC
# ------------------------
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# MEDIA
# ------------------------------------------------------------------------------
DEFAULT_FILE_STORAGE = "fahari.utils.storages.MediaRootGoogleCloudStorage"
MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/media/"
WHITENOISE_MANIFEST_STRICT = False


def require_env(name: str) -> str:
    value = env(name)
    if value is None:
        print("Missing '{}' env variable".format(name))
        sys.exit(1)
    return value


# ensure that environment variables that are needed to run tests successfully are present
require_env("GOOGLE_APPLICATION_CREDENTIALS")
require_env("DJANGO_GCP_STORAGE_BUCKET_NAME")
require_env("POSTGRES_DB")
require_env("POSTGRES_USER")
require_env("POSTGRES_PASSWORD")
require_env("POSTGRES_HOST")
require_env("POSTGRES_PORT")
