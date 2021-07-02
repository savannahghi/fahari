import logging
import uuid
from collections import defaultdict
from typing import List

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.base import ModelBase
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from .constants import COUNTIES, COUNTRY_CODES

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

    def uuid_to_string(self):
        """Convert uuid field to string."""
        # uuid not supported in elastic search
        return str(self.id)

    def created_by_to_string(self):
        """Convert uuid field to string."""
        # uuid not supported in elastic search
        return str(self.created_by)

    def updated_by_to_string(self):
        """Convert uuid field to string."""
        # uuid not supported in elastic search
        return str(self.updated_by)

    def process_copy(self, copy):
        """Use in ``make_copy`` to allow for modifications before saving."""
        return copy

    def exists(self, **kwargs):
        """Determine if a similar instance already exists."""
        return self.__class__.objects.filter(pk=self.pk, **kwargs).exists()

    def get_self(self, **kwargs):
        """Return an instance with the same PK, if it exists."""
        try:
            return self.__class__.objects.get(pk=self.pk, **kwargs)
        except self.__class__.DoesNotExist:
            return False

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
    created_by = models.UUIDField()
    updated_by = models.UUIDField()

    def uuid_to_string(self):
        """Convert uuid field to string."""
        # uuid not supported in elastic search
        return str(self.id)

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

    def natural_key(self):
        """Emit a natural key when serializing data.

        original output --> organisation: "7b36cbdd-71f1-478a-9904-621fc3a1bf"
        new output --> organisation: "CM1206"
        """
        return self.code

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
                if value:
                    if str(self.organisation.id) != str(value.organisation.id):
                        LOGGER.error(f"{field} has an inconsistent org")
                        raise ValidationError({"organisation": _(error_msg)})

    class Meta(OwnerlessAbstractBase.Meta):
        """Define a sensible default ordering."""

        abstract = True


class MLEBase(AbstractBase):
    """Base model for monitoring, learning and evaluation models."""

    class Meta(AbstractBase.Meta):
        """Define a sensible default ordering."""

        abstract = True


class Facility(AbstractBase):
    """A facility with M&E reporting."""

    name = models.TextField()
    mfl_code = models.IntegerField()
    county = models.CharField(choices=COUNTIES, max_length=24)
