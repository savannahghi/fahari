import logging
import uuid
from collections import defaultdict
from fractions import Fraction
from typing import List, Tuple, TypeVar

from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.db.models.base import ModelBase
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from PIL import Image

from ..constants import CONTENT_TYPES
from .organisation_models import Organisation
from .utils import get_directory, is_image_type, unique_list

LOGGER = logging.getLogger(__file__)
T_OA = TypeVar("T_OA", bound="OwnerlessAbstractBase", covariant=True)


# =============================================================================
# QUERYSETS
# =============================================================================


class OwnerlessAbstractBaseQuerySet(models.QuerySet[T_OA]):  # noqa
    """Base queryset for all models not linked to an organisation."""

    def active(self):
        """Return all records marked as active."""
        return self.filter(active=True)

    def non_active(self):
        """Return all records marked as non active."""
        return self.filter(active=False)


class AbstractBaseQuerySet(OwnerlessAbstractBaseQuerySet[T_OA]):  # noqa
    """Base queryset for all models linked to an organisation."""

    ...


# =============================================================================
# MANAGERS
# =============================================================================


class OwnerlessAbstractBaseManager(models.Manager[T_OA]):  # noqa
    """Base manager for all models not linked to an organisation."""

    use_for_related_fields = True
    use_in_migrations = True

    def active(self):
        """Return all the records marked as active."""
        return self.get_queryset().active()

    def get_queryset(self):
        return OwnerlessAbstractBaseQuerySet(self.model, using=self.db)  # pragma: nocover

    def non_active(self):
        """Return all the records marked as non-active."""
        return self.get_queryset().non_active()


class AbstractBaseManager(OwnerlessAbstractBaseManager[T_OA]):  # noqa
    """Base queryset for all models linked to an organisation."""

    use_for_related_fields = True
    use_in_migrations = True

    def get_queryset(self):
        return AbstractBaseQuerySet(self.model, using=self.db)


# =============================================================================
# META CLASSES
# =============================================================================


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


# =============================================================================
# BASE CLASSES
# =============================================================================


class OwnerlessAbstractBase(models.Model, metaclass=ValidationMetaclass):
    """Base class for models that are not linked to an organisation."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(default=timezone.now)
    created_by = models.UUIDField(null=True, blank=True)
    updated = models.DateTimeField(default=timezone.now)
    updated_by = models.UUIDField(null=True, blank=True)

    objects = OwnerlessAbstractBaseManager()

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
        ordering: Tuple[str, ...] = ("-updated", "-created")


class AbstractBase(OwnerlessAbstractBase):
    """Base class for most models in the application."""

    # this differs from Ownerless Abstract Base only in adding the organisation
    # field
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_related",
    )

    objects = AbstractBaseManager()

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
        error_msg = (
            "The organisation provided is not consistent with that of organisation fields in "
            "related resources"
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

    def __str__(self):
        """Represent an attachment by its title."""
        return self.title

    class Meta:
        """Declare Attachment as an abstract model."""

        ordering = ("-updated", "-created")
        abstract = True
