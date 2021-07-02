from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TreatmentConfig(AppConfig):
    name = "pepfar_mle.treatment"
    verbose_name = _("Treatment")
