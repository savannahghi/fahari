from django.urls import path

from .views import FacilityView, SystemsView

app_name = "common"
urlpatterns = [
    path("facilities", view=FacilityView.as_view(), name="facilities"),
    path("systems", view=SystemsView.as_view(), name="systems"),
]
