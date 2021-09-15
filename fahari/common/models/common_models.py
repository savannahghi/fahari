from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.urls import reverse

from ..constants import WHITELIST_COUNTIES
from ..utils import (
    get_constituencies,
    get_counties,
    get_sub_counties,
    get_wards,
    has_constituency,
    has_sub_county,
    has_ward,
)
from .base_models import AbstractBase, AbstractBaseManager, AbstractBaseQuerySet, Attachment

User = get_user_model()


# =============================================================================
# QUERYSETS
# =============================================================================


class FacilityQuerySet(AbstractBaseQuerySet):
    """Queryset for the Facility model."""

    def fahari_facilities(self):
        """Return all the facilities that are part of the FYJ program."""
        return self.active().filter(
            is_fahari_facility=True, operation_status="Operational", county__in=WHITELIST_COUNTIES
        )


# =============================================================================
# MANAGERS
# =============================================================================


class FacilityManager(AbstractBaseManager):
    """Manager for the UserFacilityAllotment model."""

    def fahari_facilities(self):
        """Return all the facilities that are part of the FYJ program."""
        return self.get_queryset().fahari_facilities()

    def get_queryset(self):
        return FacilityQuerySet(self.model, using=self.db)


# =============================================================================
# MODELS
# =============================================================================


class Facility(AbstractBase):
    """A facility with M&E reporting.

    The data is fetched - and updated - from the Kenya Master Health Facilities List.
    """

    class KEPHLevels(models.TextChoices):
        """The different Kenya Package for Health (KEPH) levels.

        This are the different tiers of health care delivery systems as
        defined by the Ministry of Health.
        """

        LEVEL_1 = "Level 1", "Level 1"
        LEVEL_2 = "Level 2", "Level 2"
        LEVEL_3 = "Level 3", "Level 3"
        LEVEL_4 = "Level 4", "Level 4"
        LEVEL_5 = "Level 5", "Level 5"
        LEVEL_6 = "Level 6", "Level 6"

    class FacilityOwnerType(models.TextChoices):
        """The different types of medical facility ownerships."""

        PRIVATE_PRACTICE = "Private Practice", "Private Practice"
        MINISTRY_OF_HEALTH = "Ministry of Health", "Ministry of Health"
        FAITH_BASED_ORG = "Faith Based Organization", "Faith Based Organization"
        NON_GOVERNMENT_ORG = "Non-Governmental Organizations", "Non-Governmental Organizations"

    class FacilityType(models.TextChoices):
        """The different types of facility types."""

        BASIC_HEALTH_CENTER = "Basic Health Centre", "Basic Health Centre"
        CTTRH = (
            "Comprehensive Teaching & Tertiary Referral Hospital",
            "Comprehensive Teaching & Tertiary Referral Hospital",
        )
        COMPREHENSIVE_HEALTH_CENTRE = "Comprehensive health Centre", "Comprehensive health Centre"
        DENTAL_CLINIC = "Dental Clinic", "Dental Clinic"
        DIALYSIS_CENTER = "Dialysis Center", "Dialysis Center"
        DCPO = (
            "Dispensaries and clinic-out patient only",
            "Dispensaries and clinic-out patient only",
        )
        DISPENSARY = "Dispensary", "Dispensary"
        FAREWELL_HOME = "Farewell Home", "Farewell Home"
        HEALTH_CENTRE = "Health Centre", "Health Centre"
        LABORATORY = "Laboratory", "Laboratory"
        MEDICAL_CENTER = "Medical Center", "Medical Center"
        MEDICAL_CLINIC = "Medical Clinic", "Medical Clinic"
        NURSING_HOMES = "Nursing Homes", "Nursing Home"
        NURSING_AND_MATERNITY_HOME = "Nursing and Maternity Home", "Nursing and Maternity Home"
        OPHTHALMOLOGY = "Ophthalmology", "Ophthalmology"
        PHARMACY = "Pharmacy", "Pharmacy"
        PRIMARY_CARE_HOSPITAL = "Primary care hospitals", "Primary care hospital"
        RADIOLOGY_CLINIC = "Radiology Clinic", "Radiology Clinic"
        RCDASA = (
            "Rehab. Center - Drug and Substance abuse",
            "Rehab. Center - Drug and Substance abuse",
        )
        SECONDARY_CARE_HOSPITAL = "Secondary care hospitals", "Secondary care hospital"
        STRH = (
            "Specialized & Tertiary Referral hospitals",
            "Specialized & Tertiary Referral hospital",
        )
        VCT = "VCT", "VCT"

    class FacilityTypeCategory(models.TextChoices):
        """The different types of facility type categories."""

        DISPENSARY = "DISPENSARY", "Dispensary"
        HEALTH_CENTRE = "HEALTH CENTRE", "Health Centre"
        HOSPITAL = "HOSPITALS", "Hospital"
        MEDICAL_CENTER = "MEDICAL CENTER", "Medical Center"
        MEDICAL_CLINIC = "MEDICAL CLINIC", "Medical Clinic"
        NURSING_HOME = "NURSING HOME", "Nursing Home"
        PRIMARY_HEALTH_CARE_SERVICES = (
            "Primary health  care services",
            "Primary Health Care Service",
        )
        STAND_ALONE = "STAND ALONE", "Stand Alone"

    name = models.TextField(unique=True)
    mfl_code = models.IntegerField(unique=True, help_text="MFL Code")
    county = models.CharField(max_length=64, choices=get_counties())
    sub_county = models.CharField(max_length=64, null=True, blank=True, choices=get_sub_counties())
    constituency = models.CharField(
        max_length=64, null=True, blank=True, choices=get_constituencies()
    )
    ward = models.CharField(max_length=64, null=True, blank=True, choices=get_wards())
    operation_status = models.CharField(max_length=24, default="Operational")
    registration_number = models.CharField(max_length=64, null=True, blank=True)
    keph_level = models.CharField(max_length=12, choices=KEPHLevels.choices, null=True, blank=True)
    facility_type = models.CharField(
        max_length=64, null=True, blank=True, choices=FacilityType.choices
    )
    facility_type_category = models.CharField(
        max_length=64, null=True, blank=True, choices=FacilityTypeCategory.choices
    )
    facility_owner = models.CharField(max_length=64, null=True, blank=True)
    owner_type = models.CharField(
        max_length=64, null=True, choices=FacilityOwnerType.choices, blank=True
    )
    regulatory_body = models.CharField(max_length=64, null=True, blank=True)
    beds = models.IntegerField(default=0)
    cots = models.IntegerField(default=0)
    open_whole_day = models.BooleanField(default=False)
    open_public_holidays = models.BooleanField(default=False)
    open_weekends = models.BooleanField(default=False)
    open_late_night = models.BooleanField(default=False)
    approved = models.BooleanField(default=True)
    public_visible = models.BooleanField(default=True)
    closed = models.BooleanField(default=False)
    lon = models.FloatField(default=0.0)
    lat = models.FloatField(default=0.0)
    is_fahari_facility = models.BooleanField(default=True)

    objects = FacilityManager()

    model_validators = [
        "check_facility_name_longer_than_three_characters",
        "check_constituency_belongs_to_selected_county",
        "check_sub_county_belongs_to_selected_county",
        "check_ward_belongs_to_selected_sub_county",
    ]

    def get_absolute_url(self):
        update_url = reverse("common:facility_update", kwargs={"pk": self.pk})
        return update_url

    def check_facility_name_longer_than_three_characters(self):
        if len(self.name) < 3:
            raise ValidationError("the facility name should exceed 3 characters")

    def check_constituency_belongs_to_selected_county(self):
        if self.constituency and not has_constituency(self.county, self.constituency):
            raise ValidationError(
                {
                    "constituency": '"{}" constituency does not belong to "{}" county'.format(
                        self.constituency, self.county
                    )
                }
            )

    def check_sub_county_belongs_to_selected_county(self):
        if self.sub_county and not has_sub_county(self.county, self.sub_county):
            raise ValidationError(
                {
                    "sub_county": '"{}" sub county does not belong to "{}" county'.format(
                        self.sub_county, self.county
                    )
                }
            )

    def check_ward_belongs_to_selected_sub_county(self):
        if self.ward and not self.sub_county:
            raise ValidationError(
                {
                    "ward": 'the sub county in which "{}" ward belongs to must be provided'.format(
                        self.ward
                    )
                }
            )
        elif self.ward and self.sub_county and not has_ward(self.sub_county, self.ward):
            raise ValidationError(
                {
                    "ward": '"{}" ward does not belong to "{}" sub county'.format(
                        self.ward, self.sub_county
                    )
                }
            )

    def __str__(self):
        return f"{self.name} - {self.mfl_code} ({self.county})"

    class Meta(AbstractBase.Meta):
        verbose_name_plural = "facilities"


class FacilityAttachment(Attachment):
    """Any document attached to a facility."""

    facility = models.ForeignKey(Facility, on_delete=models.PROTECT)
    notes = models.TextField()

    organisation_verify = ["facility"]

    class Meta(AbstractBase.Meta):
        """Define ordering and other attributes for attachments."""

        ordering = ("-updated", "-created")


class FacilityUser(AbstractBase):
    """A user assigned to a facility."""

    facility = models.ForeignKey(Facility, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    def get_absolute_url(self):
        update_url = reverse("common:facility_user_update", kwargs={"pk": self.pk})
        return update_url

    def __str__(self) -> str:
        return f"User: {self.user.name}; Facility: {self.facility.name}"

    class Meta(AbstractBase.Meta):
        """Define ordering and other attributes for attachments."""

        ordering = ("-updated", "-created")


class System(AbstractBase):
    """List of systems used in the public sector e.g Kenya EMR."""

    class SystemPatters(models.TextChoices):
        """The different patters of a system in a facility."""

        POINT_OF_CARE = "poc", "Point of Care"
        RETROSPECTIVE_DATA_ENTRY = "rde", "Retrospective Data Entry"
        HYBRID = "hybrid", "Hybrid"
        NONE = "none", "None"

    name = models.CharField(max_length=128, null=False, blank=False, unique=True)
    pattern = models.CharField(
        max_length=100, choices=SystemPatters.choices, default=SystemPatters.NONE.value
    )
    description = models.TextField()

    def get_absolute_url(self):
        update_url = reverse("common:system_update", kwargs={"pk": self.pk})
        return update_url

    def __str__(self) -> str:
        return self.name

    class Meta(AbstractBase.Meta):
        ordering = (
            "name",
            "-updated",
        )


class UserFacilityAllotment(AbstractBase):
    """Define the allocation of a facility/facilities to a user."""

    class AllotmentType(models.TextChoices):
        """The type of facility allocation to a user."""

        BY_FACILITY = "facility", "By Facility"
        BY_REGION = "region", "By Region"
        BY_FACILITY_AND_REGION = "both", "By Both Facility and Region"

    class RegionType(models.TextChoices):
        """The type of region whose facilities are to be assigned user."""

        COUNTY = "county"
        CONSTITUENCY = "constituency"
        SUB_COUNTY = "sub_county"
        WARD = "ward"

    user = models.OneToOneField(User, on_delete=models.PROTECT)
    allotment_type = models.CharField(max_length=100, choices=AllotmentType.choices)
    region_type = models.CharField(
        max_length=20, choices=RegionType.choices, null=True, blank=True
    )
    facilities = models.ManyToManyField(Facility, blank=True)
    counties = ArrayField(
        models.CharField(max_length=150, choices=get_counties(), null=True, blank=True),
        help_text=(
            "All the facilities in the selected counties will be allocated to the selected user."
        ),
        null=True,
        blank=True,
    )
    constituencies = ArrayField(
        models.CharField(max_length=150, choices=get_constituencies(), null=True, blank=True),
        help_text=(
            "All the facilities in the selected constituencies will be allocated to the selected "
            "user."
        ),
        null=True,
        blank=True,
    )
    sub_counties = ArrayField(
        models.CharField(max_length=150, choices=get_sub_counties(), null=True, blank=True),
        help_text=(
            "All the facilities in the selected sub counties will be allocated to the selected "
            "user."
        ),
        null=True,
        blank=True,
    )
    wards = ArrayField(
        models.CharField(max_length=150, choices=get_wards(), null=True, blank=True),
        help_text=(
            "All the facilities in the selected wards will be allocated to the selected user."
        ),
        null=True,
        blank=True,
    )

    model_validators = [
        "check_region_type_is_provided_if_allot_by_region_or_both",
        "check_county_is_provided_if_region_type_is_county",
        "check_constituency_is_provided_if_region_type_is_constituency",
        "check_sub_county_is_provided_if_region_type_is_sub_county",
        "check_ward_is_provided_if_region_type_is_ward",
    ]

    def check_region_type_is_provided_if_allot_by_region_or_both(self):
        by_both = self.AllotmentType.BY_FACILITY_AND_REGION.value
        by_region = self.AllotmentType.BY_REGION.value
        if self.allotment_type in (by_both, by_region) and not self.region_type:
            raise ValidationError(
                {
                    "region_type": 'A region type must be provided if allotment type is "%s"'
                    % self.get_allotment_type_display()  # noqa
                },
                code="required",
            )

    def check_county_is_provided_if_region_type_is_county(self):
        by_both = self.AllotmentType.BY_FACILITY_AND_REGION.value
        by_region = self.AllotmentType.BY_REGION.value
        county = self.RegionType.COUNTY
        if (
            self.allotment_type in (by_both, by_region)
            and self.region_type == county.value
            and not self.counties
        ):
            raise ValidationError(
                {
                    "counties": 'At least 1 county must be selected if region type is "%s"'
                    % county.label
                },
                code="required",
            )

    def check_constituency_is_provided_if_region_type_is_constituency(self):
        by_both = self.AllotmentType.BY_FACILITY_AND_REGION.value
        by_region = self.AllotmentType.BY_REGION.value
        constituency = self.RegionType.CONSTITUENCY
        if (
            self.allotment_type in (by_both, by_region)
            and self.region_type == constituency.value
            and not self.constituencies
        ):
            raise ValidationError(
                {
                    "constituencies": "At least 1 constituency must be selected if region type "
                    'is "%s"' % constituency.label
                },
                code="required",
            )

    def check_sub_county_is_provided_if_region_type_is_sub_county(self):
        by_both = self.AllotmentType.BY_FACILITY_AND_REGION.value
        by_region = self.AllotmentType.BY_REGION.value
        sub_county = self.RegionType.SUB_COUNTY
        if (
            self.allotment_type in (by_both, by_region)
            and self.region_type == sub_county.value
            and not self.sub_counties
        ):
            raise ValidationError(
                {
                    "sub_counties": 'At least 1 sub_county must be selected if region type is "%s"'
                    % sub_county.label
                },
                code="required",
            )

    def check_ward_is_provided_if_region_type_is_ward(self):
        by_both = self.AllotmentType.BY_FACILITY_AND_REGION.value
        by_region = self.AllotmentType.BY_REGION.value
        ward = self.RegionType.WARD
        if (
            self.allotment_type in (by_both, by_region)
            and self.region_type == ward.value
            and not self.wards
        ):
            raise ValidationError(
                {"wards": 'At least 1 ward must be selected if region type is "%s"' % ward.label},
                code="required",
            )

    def get_absolute_url(self):
        update_url = reverse("common:user_facility_allotment_update", kwargs={"pk": self.pk})
        return update_url

    def __str__(self):
        return (
            f"User: {self.user.name}; Allotment Type: {self.get_allotment_type_display()}"  # noqa
        )

    @staticmethod
    def get_facilities_for_user(user):
        """Return a queryset containing all the facilities allotted to the given user."""

        allotment = UserFacilityAllotment.objects.filter(user=user).first()
        if not allotment:
            return Facility.objects.none()
        return UserFacilityAllotment.get_facilities_for_allotment(allotment)

    @staticmethod
    def get_facilities_for_allotment(allotment: "UserFacilityAllotment"):
        """Return a queryset containing all the facilities specified in the given allotment."""

        by_facility = UserFacilityAllotment.AllotmentType.BY_FACILITY.value
        by_region = UserFacilityAllotment.AllotmentType.BY_REGION.value

        by_facility_filter = UserFacilityAllotment._get_allot_by_facility_filter(allotment)
        by_region_filter = UserFacilityAllotment._get_allot_by_region_filter(allotment)
        facilities = Facility.objects.filter(organisation=allotment.organisation)

        if allotment.allotment_type == by_facility:
            return facilities.filter(**by_facility_filter)
        if allotment.allotment_type == by_region:
            return facilities.filter(**by_region_filter)
        # for both facility and region
        return facilities.filter(Q(**by_facility_filter) | Q(**by_region_filter))

    @staticmethod
    def _get_allot_by_facility_filter(allotment: "UserFacilityAllotment"):
        """Helper for generating a queryset filter."""

        return {"pk__in": allotment.facilities.values_list("pk", flat=True)}

    @staticmethod
    def _get_allot_by_region_filter(allotment: "UserFacilityAllotment"):
        """Helper for generating a queryset filter."""

        by_region_filter = {}
        if allotment.region_type == UserFacilityAllotment.RegionType.COUNTY.value:
            by_region_filter["county__in"] = allotment.counties
        elif allotment.region_type == UserFacilityAllotment.RegionType.CONSTITUENCY.value:
            by_region_filter["constituency__in"] = allotment.constituencies
        elif allotment.region_type == UserFacilityAllotment.RegionType.SUB_COUNTY.value:
            by_region_filter["sub_county__in"] = allotment.sub_counties
        elif allotment.region_type == UserFacilityAllotment.RegionType.WARD.value:
            by_region_filter["ward__in"] = allotment.wards

        return by_region_filter

    class Meta(AbstractBase.Meta):
        """Define ordering and other attributes for attachments."""

        ordering = ("-updated", "-created")
