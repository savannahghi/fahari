from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TBConfig(AppConfig):
    name = "fahari.tb"
    verbose_name = _("TB")
