from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TBConfig(AppConfig):
    name = "pepfar_mle.tb"
    verbose_name = _("TB")
