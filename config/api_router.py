from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from fahari.common.views import FacilityViewSet, SystemViewSet
from fahari.ops.views import FacilitySystemTicketViewSet, FacilitySystemViewSet
from fahari.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("facilities", FacilityViewSet)
router.register("systems", SystemViewSet)
router.register("versions", FacilitySystemViewSet)
router.register("tickets", FacilitySystemTicketViewSet)


app_name = "api"
urlpatterns = router.urls
