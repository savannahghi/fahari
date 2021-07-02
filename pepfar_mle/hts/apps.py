from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HTSConfig(AppConfig):
    name = "pepfar_mle.hts"
    verbose_name = _("HTS")
