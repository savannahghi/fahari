from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from fahari.common.views import FacilityUserViewSet, FacilityViewSet, SystemViewSet
from fahari.ops.views import (
    ActivityLogViewSet,
    CommodityViewSet,
    DailyUpdateViewSet,
    FacilitySystemTicketViewSet,
    FacilitySystemViewSet,
    SiteMentorshipViewSet,
    StockReceiptVerificationViewSet,
    TimeSheetViewSet,
    WeeklyProgramUpdateViewSet,
)
from fahari.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("facilities", FacilityViewSet)
router.register("facility_users", FacilityUserViewSet)
router.register("systems", SystemViewSet)
router.register("versions", FacilitySystemViewSet)
router.register("tickets", FacilitySystemTicketViewSet)
router.register("stock_receipts", StockReceiptVerificationViewSet)
router.register("activity_logs", ActivityLogViewSet)
router.register("site_mentorships", SiteMentorshipViewSet)
router.register("daily_updates", DailyUpdateViewSet)
router.register("timesheets", TimeSheetViewSet)
router.register("weekly_updates", WeeklyProgramUpdateViewSet)
router.register("commodities", CommodityViewSet)

app_name = "api"
urlpatterns = router.urls
