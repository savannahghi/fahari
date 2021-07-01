import copy
import itertools
import logging
import os
import uuid
from collections import defaultdict

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models, transaction
from django.db.models.base import ModelBase
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from pepfar_mle.transitions.mixins import TransitionAndLogMixin

from .constants import COUNTIES, COUNTRY_CODES
from .utilities import load_system_data, send_email, unique_list

LOGGER = logging.getLogger(__file__)
ORG_TRANSITION_GRAPH = {True: [False], False: [True]}


def send_email_on_org_create(organisation):
    """Email the administrator on successful creation of an organisation."""
    plain_text = "common/registration/organisation_success.txt"
    html_temp = "common/registration/organisation_success.html"
    context = {
        "organisation_name": organisation["organisation_name"],
        "organisation_email": organisation["email_address"],
    }
    subject = "You have been successfully registered."
    return send_email(
        context,
        organisation["email_address"],
        plain_text,
        html_temp,
        subject,
    )


class GetUserFullname(object):
    """Helpers to work with users."""

    def get_user_fullname(self, action_type):
        """Return ``created_by`` || ``updated_by`` full name."""
        guid = str(action_type)
        user_model = get_user_model()
        try:
            user_obj = user_model.objects.get(pk=guid)
            return user_obj.get_full_name()
        except (user_model.DoesNotExist, ValidationError):
            return None

    @property
    def made_by(self):
        """Return ``created_by`` full name."""
        return self.get_user_fullname(self.created_by)

    @property
    def updated_by_name(self):
        """Return ``updated_by`` full name."""
        return self.get_user_fullname(self.updated_by)


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


class ValidationErrorsMixin(object):
    """Run all model validations and aggregate errors.

    Errors are aggregated in either of the following ways:

    - if validation error was raised with a dict, aggregate the messages under
        the relevant key
    - if validation was raised with a message / list of messages, aggregate the
        messages under __all__ key
    """

    def _raise_errors(self, errors):
        if errors:
            raise ValidationError(errors)

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
        """Run full validation with each save."""
        # the validate_unique=False is a "hack" to deal with some test
        # failures that were not properly understood. It needs to be
        # removed
        self.full_clean(validate_unique=False)
        super().save(*args, **kwargs)


class OwnerlessAbstractBase(
    ValidationErrorsMixin, models.Model, metaclass=ValidationMetaclass
):
    """Base class for models that are not linked to an organisation."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(default=timezone.now)
    created_by = models.UUIDField(null=True, blank=True)
    updated = models.DateTimeField(default=timezone.now)
    updated_by = models.UUIDField(null=True, blank=True)

    model_validators = ["validate_updated_date_greater_than_created"]

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

    @transaction.atomic
    def make_copy(self):
        """Clone an object."""
        obj = copy.copy(self)
        obj.pk = None
        obj = self.process_copy(obj)
        obj.save()
        related_objects = self._meta.related_objects
        for each in related_objects:
            instances = iter(())
            for instance in getattr(self, each.get_accessor_name()).all():
                # for a self reference field do not duplicate obj
                if instance == obj:
                    continue
                instance.pk = None
                setattr(instance, each.remote_field.name, obj)

                # Create a many to many field in sales order copy
                # Open to a better implementation...
                if (
                    instance.__class__.__name__ == "SalesOrderLine"
                    and instance.quotation_line
                ):
                    instance.sales_order.quotations.add(
                        instance.quotation_line.quotation
                    )

                instance.clean()
                instances = itertools.chain(instances, [instance])
            each.related_model.objects.bulk_create(instances)
            instances = iter(())
        return obj

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
            raise ValidationError(
                "The updated date cannot be less than the created date"
            )

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


class OrganisationTransitionLog(GetUserFullname, OrganisationAbstractBase):
    """Record every time an org changes between active and inactive."""

    active_from = models.CharField(max_length=255)
    active_to = models.CharField(max_length=255)
    organisation = models.ForeignKey(
        "Organisation",
        related_name="organisation_logs",
        on_delete=models.PROTECT,
    )
    note = models.TextField()

    def __str__(self):
        """Render note as a string representation."""
        return self.note

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Ensure correct handling of audit fields when saving an org."""
        self.updated = timezone.now()
        self.preserve_created_and_created_by()
        super().save()


class Organisation(TransitionAndLogMixin, OrganisationAbstractBase):
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

    _transition_field = "active"
    _transition_log_model_fk_field = "organisation"
    _transition_log_model = OrganisationTransitionLog
    _transition_graph = ORG_TRANSITION_GRAPH

    slade_code = models.IntegerField(unique=True)
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
    default_country = models.CharField(
        max_length=255, choices=COUNTRY_CODES, default="KEN"
    )
    # strict workstation filter specifies whether when displaying branches,
    # departments, stores, workstation et al, the user's view should be
    # limited to what is in the organisation unit the workstation they
    # are logged into is attached to.
    strict_workstation_filter = models.BooleanField(default=False)
    financial_year_start_date = models.DateField()

    def __str__(self):
        """Represent an organisation using it's name."""
        return self.organisation_name

    def natural_key(self):
        """Emit a natural key when serializing data.

        original output --> organisation: "7b36cbdd-71f1-478a-9904-621fc3a1bf"
        new output --> organisation: "CM1206"
        """
        return self.slade_code

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

    def _setup_default_user(self):
        from sil.common.models import Person, UserProfile

        person = {
            "first_name": self.organisation_name,
            "last_name": "Admin",
            "organisation": self,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
        }
        user_data = {"guid": uuid.uuid4(), "email": self.email_address}
        person = Person.objects.create(**person)
        user = get_user_model().objects.create_user(**user_data)
        UserProfile.objects.create(
            user=user,
            person=person,
            organisation=self,
            created_by=self.created_by,
            updated_by=self.updated_by,
        )
        return user

    def send_new_client_email(self):
        """Send email on first creation."""
        org_instance = {
            "id": str(self.pk),
            "email_address": self.email_address,
            "organisation_name": self.organisation_name,
        }
        send_email_on_org_create(org_instance)

    def create_financial_year(self):
        """Ensure that an organisation has a financial year."""
        # late import coz of financial year's this model dependecy
        from sil.common.models.financial_year import FinancialYear

        # at point of creating organisation, there shouldn't be any
        # existing financial years in the system for that organisation.
        # so we delete any that could be in the system.
        # this also helps us ensure you do not have contradicting
        # financial year start which is specified when creating organisation.

        FinancialYear.objects.filter(organisation=self).delete()
        return FinancialYear.create_financial_year(self, self.updated_by)

    @property
    def default_currency(self):
        """Ensure that an organisation has a currency."""
        try:
            return self.common_currency_related.get(is_default=True)
        except ObjectDoesNotExist:
            return self.create_default_currency()

    @property
    def active_financial_year(self):
        """Return the organisation's active financial year."""
        from sil.common.models.financial_year import FinancialYear

        return FinancialYear.get_active_financial_year(self)

    @property
    def current_financial_year(self):
        """Determine the current financial year."""
        from sil.common.models.financial_year import FinancialYear

        return FinancialYear.get_financial_year(self, timezone.now())

    @property
    def client_types(self):
        """Return the client types linked to an organisation."""
        return self.branches_orgclienttype_related.values("client_type", "id")

    def create_default_currency(self):
        """Create the default KES currency."""
        vals = {
            "name": "Kenyan Shilling",
            "iso_code": "KES",
            "is_default": True,
            "conversion_rate": 1,
            "organisation": self,
            "created_by": self.updated_by,
            "updated_by": self.updated_by,
        }
        return self.common_currency_related.create(**vals)

    def load_system_data(self):
        """Load system data and currencies."""
        data_files = os.path.join(settings.BASE_DIR, "data/system/*/*.json")
        load_system_data(data_files, self.pk, self.created_by)

    def transition(self, data):
        """Allow ``notes`` to be added to the ``OrganisationTransitionLog``."""
        self.note = data["note"]
        super().transition(data)

    def transition_log_data(self):
        """Prepare a transition log data dict that is ready to be saved."""
        data = super().transition_log_data()
        data.update(
            {
                "note": self.note,
                "created_by": self.updated_by,
                "updated_by": self.updated_by,
            }
        )
        return data

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Ensure that a newly created organisation gets system data."""
        self.updated = timezone.now()
        self.preserve_created_and_created_by()
        obj_exists = self.__class__.objects.filter(pk=self.pk)

        if not obj_exists:
            self._set_organisation_code()
        else:
            self.financial_year_start_date = obj_exists[0].financial_year_start_date

        super().save(*args, **kwargs)

        obj_existed = obj_exists

        if obj_existed:
            return self

        if self.active and not self.deleted and not settings.DISABLE_ORG_SETUP:
            d_user = self._setup_default_user()
            # set financial_year
            self.create_financial_year()
            assert self.default_currency
            self.load_system_data()

            from sil.branches.models import WorkStation, WorkStationUser

            workstation = WorkStation.objects.get(
                name="Administration", organisation=self
            )
            WorkStationUser.objects.create(
                workstation=workstation,
                health_worker=d_user,
                created_by=self.created_by,
                updated_by=self.updated_by,
                organisation=self,
            )


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


class AbstractBase(OwnerlessAbstractBase):
    """Base class for most models in the application."""

    # this differs from Ownerless Abstract Base only in adding the organisation
    # field
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_related",
    )

    organisation_verify = []
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

    pass


class Facility(AbstractBase):
    """A facility with M&E reporting."""

    name = models.TextField()
    mfl_code = models.IntegerField()
    county = models.CharField(choices=COUNTIES, max_length=24)
