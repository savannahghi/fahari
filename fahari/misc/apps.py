from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MiscConfig(AppConfig):
    name = "fahari.misc"
    verbose_name = _("Miscellaneous")
