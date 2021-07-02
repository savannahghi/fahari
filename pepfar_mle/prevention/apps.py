from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PreventionConfig(AppConfig):
    name = "pepfar_mle.prevention"
    verbose_name = _("Prevention")
