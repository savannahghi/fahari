import logging
import uuid

from django.contrib.gis.db import models
from django.db import transaction
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from ..constants import COUNTRY_CODES

LOGGER = logging.getLogger(__file__)


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

    class Meta:
        """Define a sensible default ordering for organisations."""

        ordering = ("-updated", "-created")
        abstract = False
