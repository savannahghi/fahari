from django.forms import ModelForm

from .models import Facility, FacilityAttachment, Organisation


class OrganisationForm(ModelForm):
    class Meta:
        model = Organisation
        fields = "__all__"


class FacilityForm(ModelForm):
    class Meta:
        model = Facility
        fields = "__all__"


class FacilityAttachmentForm(ModelForm):
    class Meta:
        model = FacilityAttachment
        fields = "__all__"
