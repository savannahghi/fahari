from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from fahari.common.views import FacilityViewSet
from fahari.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("facilities", FacilityViewSet)


app_name = "api"
urlpatterns = router.urls
