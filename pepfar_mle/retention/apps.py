from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RetentionConfig(AppConfig):
    name = "pepfar_mle.retention"
    verbose_name = _("Retention")
