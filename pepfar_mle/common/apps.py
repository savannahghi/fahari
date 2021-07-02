from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CommonConfig(AppConfig):
    name = "pepfar_mle.common"
    verbose_name = _("Common")
