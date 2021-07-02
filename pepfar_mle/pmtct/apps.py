from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PMTCTConfig(AppConfig):
    name = "pepfar_mle.pmtct"
    verbose_name = _("PMTCT")
