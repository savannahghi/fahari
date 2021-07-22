import logging
import uuid
from collections import defaultdict
from fractions import Fraction
from typing import List

from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models.base import ModelBase
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image

from .constants import CONTENT_TYPES, COUNTRY_CODES, IMAGE_TYPES

LOGGER = logging.getLogger(__file__)


def unique_list(list_object):
    """Return a list that contains only unique items."""
    seen = set()
    new_list = []
    for each in list_object:
        if each in seen:
            continue
        new_list.append(each)
        seen.add(each)

    return new_list


def get_directory(instance, filename):
    """Determine the upload_to path for every model inheriting Attachment."""
    org = instance.organisation.organisation_name
    return "{}/{}/{}".format(org, instance.__class__.__name__.lower(), filename)


def is_image_type(file_type):
    """Check if file is an image."""
    return file_type in IMAGE_TYPES


class ValidationMetaclass(ModelBase):
    """Ensures model_validators defined in parent are retained in child models.

    For example:

        class Parent(models.Model):
            model_validators = ["a"]

        class Child(models.Model(Parent):
            model_validators = ["b"]

        assert Child().model_validators == ["a", "b"]  # True
    """

    def __new__(cls, name, bases, attrs):
        """Customize the model metaclass - add support for model_validators."""
        _model_validators = []
        for each in bases:
            if hasattr(each, "model_validators"):
                _model_validators.extend(each.model_validators)
        _model_validators.extend(attrs.get("model_validators", []))
        attrs["model_validators"] = _model_validators
        return super(ValidationMetaclass, cls).__new__(cls, name, bases, attrs)


class OwnerlessAbstractBase(models.Model, metaclass=ValidationMetaclass):
    """Base class for models that are not linked to an organisation."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(default=timezone.now)
    created_by = models.UUIDField(null=True, blank=True)
    updated = models.DateTimeField(default=timezone.now)
    updated_by = models.UUIDField(null=True, blank=True)

    model_validators = ["validate_updated_date_greater_than_created"]

    def _raise_errors(self, errors):
        if errors:
            raise ValidationError(errors)

    def validate_updated_date_greater_than_created(self):
        """Ensure that updated is always after created."""
        if self.updated and self.created and self.updated.date() < self.created.date():
            # using dates to avoid a lot of fuss about milliseconds etc
            raise ValidationError("The updated date cannot be less than the created date")

    def preserve_created_and_created_by(self):
        """Ensure that in created and created_by fields are not overwritten."""
        try:
            original = self.__class__.objects.get(pk=self.pk)
            self.created = original.created
            self.created_by = original.created_by
        except self.__class__.DoesNotExist:
            LOGGER.debug(
                "preserve_created_and_created_by "
                "Could not find an instance of {} with pk {} hence treating "
                "this as a new record.".format(self.__class__, self.pk)
            )

    def run_model_validators(self):
        """Ensure that all model validators run."""
        validators = getattr(self, "model_validators", [])
        self.run_validators(validators)

    def run_validators(self, validators):
        """Run declared model validators."""
        errors = defaultdict(list)

        for validator in unique_list(validators):
            try:
                getattr(self, validator)()
            except ValidationError as e:
                if hasattr(e, "error_dict"):
                    for key, messages in e.message_dict.items():
                        # messages is ValidationError instances list
                        errors[key].extend(messages)
                else:
                    errors["__all__"].extend(e.messages)

        self._raise_errors(errors)

    def clean(self):
        """Run validators declared under model_validators."""
        self.run_model_validators()
        super().clean()

    def save(self, *args, **kwargs):
        """Handle audit fields correctly when saving."""
        self.updated = timezone.now() if self.updated is None else self.updated
        self.preserve_created_and_created_by()
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        """Define a sensible default ordering."""

        abstract = True
        ordering = ("-updated", "-created")


class OrganisationSequenceGenerator(models.Model):
    """
    Exists only to enable reliable DB agnostic sequential code generation.

    The organisation model will obtain the 'next available sequence'
    by saving an instance of this class and getting back it's primary key.

    This technique will work across all databases that Django supports.It
    is essential also for ensuring that tests can be done in-memory in
    SQLIte with minimum fuss.
    """


def _get_next_organisation_code_in_sequence():
    """Intended to be used as a callable for the organisation code default."""
    seq = OrganisationSequenceGenerator.objects.create()
    return seq.pk


class OrganisationAbstractBase(models.Model):
    """Base class for Organisation."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)
    created_by = models.UUIDField(blank=True, null=True)
    updated_by = models.UUIDField(blank=True, null=True)

    def preserve_created_and_created_by(self):
        """Ensure that created and created_by values are not overwritten."""
        try:
            original = self.__class__.objects.get(pk=self.pk)
            self.created = original.created
            self.created_by = original.created_by
        except self.__class__.DoesNotExist:
            LOGGER.debug(
                "preserve_created_and_created_by "
                "Could not find an instance of {} with pk {} hence treating "
                "this as a new record.".format(self.__class__, self.pk)
            )

    class Meta:
        """Define a sensible default ordering for organisations."""

        ordering = ("-updated", "-created")
        abstract = True


class Organisation(OrganisationAbstractBase):
    """
    Define organisations - the main unit of partitioning.

    All resources besides the system resources have an organisation.
    The organisation is the single 'special' resource in the entire system.
    It does **not** descend from the base class as in other apps.

    This is considered a worthwhile trade-off because this resource is to be
    maintained only by the overall system administrator. Breaking the link
    between this and the base class helps avoid cyclic dependencies
    in migrations.
    """

    code = models.IntegerField(unique=True)
    active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    org_code = models.CharField(
        max_length=15,
        unique=True,
        editable=False,
        help_text="A unique code representing organisation registration",
        default="",
    )
    organisation_name = models.CharField(max_length=100, unique=True)

    # To be used by Branches, Departments and Department units
    # Branches belong to a certain organisation
    email_address = models.EmailField(max_length=100)
    phone_number = PhoneNumberField()
    description = models.TextField(null=True, blank=True)
    postal_address = models.CharField(max_length=100, blank=True)
    physical_address = models.TextField(blank=True)
    default_country = models.CharField(max_length=255, choices=COUNTRY_CODES, default="KEN")

    def __str__(self):
        """Represent an organisation using it's name."""
        return self.organisation_name

    def _set_organisation_code(self):
        code_sequence = _get_next_organisation_code_in_sequence()
        pad_code = str(code_sequence).zfill(4)
        filtered_org_name = "".join(
            c for c in self.organisation_name if c not in r"\?:!/();$%^&*)"
        )
        count = len(self.organisation_name.split())
        if count >= 2:
            first_letters = [i[0].upper() for i in filtered_org_name.split()]
            name = "".join(first_letters)

            self.org_code = "ORG" + "-" + name[:2].upper() + "-" + pad_code
        else:
            words = [i for i in filtered_org_name.split()]
            joined = "".join(words)
            self.org_code = "ORG" + "-" + joined[:2].upper() + "-" + pad_code

        return self.org_code

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Ensure that a newly created organisation gets system data."""
        self.updated = timezone.now()
        self.preserve_created_and_created_by()
        obj_exists = self.__class__.objects.filter(pk=self.pk)

        if not obj_exists:
            self._set_organisation_code()

        super().save(*args, **kwargs)

        obj_existed = obj_exists

        if obj_existed:
            return self


class AbstractBase(OwnerlessAbstractBase):
    """Base class for most models in the application."""

    # this differs from Ownerless Abstract Base only in adding the organisation
    # field
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_related",
    )

    organisation_verify: List[str] = []
    model_validators = [
        "validate_organisation",
        "validate_updated_date_greater_than_created",
    ]

    @property
    def owner(self):
        """Return the record's owner."""
        return self.organisation.org_code

    def validate_organisation(self):
        """Verify that orgs in FKs are consistent with those being created."""
        error_msg = " ".join(
            [
                "The organisation provided is not consistent",
                "with that of organisation fields in",
                "related resources",
            ]
        )
        if self.organisation_verify:
            for field in self.organisation_verify:
                value = getattr(self, field)
                if value and str(self.organisation.id) != str(value.organisation.id):
                    LOGGER.error(f"{field} has an inconsistent org")
                    raise ValidationError({"organisation": _(error_msg)})

    class Meta(OwnerlessAbstractBase.Meta):
        """Define a sensible default ordering."""

        abstract = True


class Attachment(AbstractBase):
    """Shared model for all attachments."""

    content_type = models.CharField(max_length=100, choices=CONTENT_TYPES)
    data = models.FileField(upload_to=get_directory, max_length=65535)
    title = models.CharField(max_length=255)
    creation_date = models.DateTimeField(default=timezone.now)
    size = models.IntegerField(
        help_text="The size of the attachment in bytes", null=True, blank=True
    )
    description = models.TextField(null=True, blank=True)
    aspect_ratio = models.CharField(max_length=50, blank=True, null=True)

    model_validators = ["validate_image_size"]

    def validate_image_size(self):
        """Ensure that the supplied image size matches the actual file."""
        if not is_image_type(self.content_type):
            return

        image = Image.open(self.data)
        self.size = len(image.fp.read())

        width, height = image.size
        msg_template = (
            "Your image has a {axis} of {actual_size} {extra_text} "
            "pixels which is larger than allowable dimension of "
            "{expected_size} pixels."
        )
        msg = None
        if height > settings.MAX_IMAGE_HEIGHT:
            msg = msg_template.format(
                axis="height",
                actual_size=height,
                expected_size=settings.MAX_IMAGE_HEIGHT,
                extra_text="{extra_text}",
            )

        if width > settings.MAX_IMAGE_WIDTH:
            msg = (
                msg.format(extra_text="and width of {}".format(width))
                if msg
                else msg_template.format(
                    axis="width",
                    actual_size=width,
                    expected_size=settings.MAX_IMAGE_WIDTH,
                    extra_text="",
                )
            )

        if msg:
            msg = msg.format(extra_text="")
            raise ValidationError(msg)

        # Set the image aspect ratio
        float_ratio = float(width / height)
        fraction_ratio = str(Fraction(float_ratio).limit_denominator())
        self.aspect_ratio = fraction_ratio.replace("/", ":")

    class Meta:
        """Declare Attachment as an abstract model."""

        ordering = ("-updated", "-created")
        abstract = True

    def __str__(self):
        """Represent an attachment by its title."""
        return self.title


class Facility(AbstractBase):
    """A facility with M&E reporting.

    The data is fetched - and updated - from the Kenya Master Health Facilities List.
    """

    name = models.TextField(unique=True)
    mfl_code = models.IntegerField(unique=True)
    county = models.CharField(max_length=64)
    sub_county = models.CharField(max_length=64, null=True, blank=True)
    constituency = models.CharField(max_length=64, null=True, blank=True)
    ward = models.CharField(max_length=64, null=True, blank=True)
    operation_status = models.CharField(max_length=24, default="Operational")
    registration_number = models.CharField(max_length=64, null=True, blank=True)
    keph_level = models.CharField(max_length=12, null=True, blank=True)
    facility_type = models.CharField(max_length=64, null=True, blank=True)
    facility_type_category = models.CharField(max_length=64, null=True, blank=True)
    facility_owner = models.CharField(max_length=64, null=True, blank=True)
    owner_type = models.CharField(max_length=64, null=True, blank=True)
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

    model_validators = [
        "facility_name_longer_than_three_characters",
    ]

    def facility_name_longer_than_three_characters(self):
        if len(self.name) < 3:
            raise ValidationError("the facility name should exceed 3 characters")

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


class System(AbstractBase):
    """List of systems used in the public sector e.g Kenya EMR."""

    name = models.CharField(max_length=128, null=False, blank=False, unique=True)
    description = models.TextField()

    class Meta(AbstractBase.Meta):
        ordering = (
            "name",
            "-updated",
        )
