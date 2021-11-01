from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from fahari.common.views import FacilityViewSet, SystemViewSet, UserFacilityViewSet
from fahari.misc.views import StockVerificationReceiptsAdapterView
from fahari.ops.views import (
    ActivityLogViewSet,
    CommodityViewSet,
    DailyUpdateViewSet,
    FacilityDeviceRequestViewSet,
    FacilityDeviceViewSet,
    FacilityNetworkStatusViewSet,
    FacilitySystemTicketViewSet,
    FacilitySystemViewSet,
    MentorshipQuestionnaireViewSet,
    MentorshipTeamViewSet,
    QuestionGroupViewSet,
    QuestionnaireViewSet,
    QuestionViewSet,
    SecurityIncidenceViewSet,
    SiteMentorshipViewSet,
    StockReceiptVerificationViewSet,
    TimeSheetViewSet,
    UoMCategoryViewSet,
    UoMViewSet,
    WeeklyProgramUpdateCommentsViewSet,
    WeeklyProgramUpdateViewSet,
)
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
router.register("stock_receipts", StockReceiptVerificationViewSet)
router.register("activity_logs", ActivityLogViewSet)
router.register("site_mentorships", SiteMentorshipViewSet)
router.register("daily_updates", DailyUpdateViewSet)
router.register("timesheets", TimeSheetViewSet)
router.register("weekly_updates", WeeklyProgramUpdateViewSet)
router.register("weekly_update_comments", WeeklyProgramUpdateCommentsViewSet)
router.register("commodities", CommodityViewSet)
router.register("uoms", UoMViewSet)
router.register("uom_categories", UoMCategoryViewSet)
router.register("user_facility_allotments", UserFacilityViewSet)
router.register("network_status", FacilityNetworkStatusViewSet)
router.register("facility_devices", FacilityDeviceViewSet)
router.register("facility_device_requests", FacilityDeviceRequestViewSet)
router.register("security_incidents", SecurityIncidenceViewSet)
router.register("stock_receipts_adapters", StockVerificationReceiptsAdapterView)
router.register("questions", QuestionViewSet)
router.register("question_group", QuestionGroupViewSet)
router.register("mentorship_team", MentorshipTeamViewSet)
router.register("questionnaires", QuestionnaireViewSet)
router.register("mentorship_questionnaires", MentorshipQuestionnaireViewSet)
app_name = "api"
urlpatterns = router.urls
