import logging
import uuid
from collections import defaultdict
from fractions import Fraction
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, TypeVar

from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models.base import ModelBase
from django.db.models.constraints import BaseConstraint
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from PIL import Image

from ..constants import CONTENT_TYPES
from .organisation_models import Organisation
from .utils import get_directory, is_image_type, unique_list

LOGGER = logging.getLogger(__file__)
T_OA = TypeVar("T_OA", bound="OwnerlessAbstractBase", covariant=True)
T_LR = TypeVar("T_LR", bound="LinkedRecordsBase", covariant=True)


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


class LinkedRecordsQuerySet(AbstractBaseQuerySet[T_LR]):  # noqa
    """Base queryset for all models that form linked records."""

    def leaf_nodes(self):
        """Return all the records that are leaf nodes for a given model."""
        # TODO: Make sure this works
        return self.exclude(
            pk__in=self.filter(previous_node__isnull=False).values("previous_node")
        )

    def root_nodes(self):
        """Return all the records that form root nodes for a given model."""
        return self.filter(previous_node=None)


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
    """Base manager for all models linked to an organisation."""

    use_for_related_fields = True
    use_in_migrations = True

    def get_queryset(self):
        return AbstractBaseQuerySet(self.model, using=self.db)


class LinkedRecordsManager(AbstractBaseManager[T_LR]):  # noqa
    """Base manager used by all models that form linked records."""

    _DISTINCT_FIELDS_UNIQUE_CONSTRAINT_NAME = "unique_distinct_fields"
    _PREVIOUS_NODE_UNIQUE_CONSTRAINT_NAME = "unique_%(app_label)s.%(class)s_previous_node"

    def __init__(self, distinct_fields: Optional[Sequence[str]] = None):
        super().__init__()
        self._distinct_fields = distinct_fields or ("pk",)

    def contribute_to_class(self, model: Type[models.Model], name: str) -> None:
        """Extend the default behaviour to add a unique constraint for the previous node."""
        super().contribute_to_class(model, name)
        model._meta.constraints = [*model._meta.constraints, *self.get_previous_node_constraints()]

    def create_root_node(self, *args, **kwargs):
        """Create and return a root node with the given properties."""

        kwargs["previous_node"] = None
        return super().create(*args, **kwargs)

    def create_leaf_node(self, **kwargs):
        """Create and return a leaf node with the given properties.

        This node will automatically be appended to the end of it's link when
        one exists. If one doesn't exist, then it will be the root node in
        it's new link.
        """

        leaf_node = self.leaf_node(**kwargs)
        kwargs["previous_node"] = leaf_node
        return super().create(**kwargs)

    def get_distinct_fields(self) -> Sequence[str]:
        """Return a sequence of all the field names used to distinguish links within records."""

        return self._distinct_fields

    def get_previous_node_constraints(self) -> Sequence[BaseConstraint]:
        """Return unique constraint(s) used to ensure uniqueness of previous nodes within a link.

        The default implementation of this method returns a unique constraint
        consisting of all the distinct fields plus the `previous_node` field.
        """
        constraint_name = self._PREVIOUS_NODE_UNIQUE_CONSTRAINT_NAME % {
            "app_label": self.model._meta.app_label.lower(),
            "class": self.model.__name__.lower(),
        }
        return (
            models.UniqueConstraint(
                name=constraint_name,
                deferrable=models.Deferrable.DEFERRED,  # noqa
                fields=(*self.get_distinct_fields(), "previous_node"),
            ),
            # This is needed to ensure that there can only be one set of distinct
            # field's values where `previous_node` is null. That is, there can
            # only be one root node per link.
            #
            # This is disabled right now to allow existing records to be linked
            # together correctly. Once that is done, this can be enabled.
            # models.UniqueConstraint(
            #     name=self._DISTINCT_FIELDS_UNIQUE_CONSTRAINT_NAME,
            #     condition=models.Q(previous_node__isnull=True),
            #     fields=(*self.get_distinct_fields(),)
            # )
        )

    def get_queryset(self):
        """Override the default queryset to use LinkedRecordsQuerySet instances."""

        return LinkedRecordsQuerySet(self.model, using=self.db)

    def leaf_node(self, **distinct_values) -> Optional["LinkedRecordsBase"]:
        """"""

        return self.nodes(**distinct_values).leaf_nodes().first()

    def leaf_nodes(self) -> "LinkedRecordsQuerySet":
        return self.get_queryset().leaf_nodes()

    def nodes(self, **distinct_values) -> "LinkedRecordsQuerySet":
        qs_filter = self._get_link_filter(**distinct_values)
        return self.get_queryset().filter(**qs_filter)

    def root_node(self, **distinct_values) -> Optional["LinkedRecordsBase"]:
        return self.nodes(**distinct_values).root_nodes().first()

    def root_nodes(self) -> "LinkedRecordsQuerySet":
        return self.get_queryset().root_nodes()

    def _ensure_valid_distinct_values(self, **distinct_values):
        # TODO: Make sure that the distinct values are what we expect
        keys = set(distinct_values.keys())
        fields = set(self.get_distinct_fields())
        differences = fields - keys
        if differences:
            raise ValueError('The fields: "%s" are required.' % ", ".join(differences))

    def _get_link_filter(self, **distinct_values) -> Dict[str, Any]:
        self._ensure_valid_distinct_values(**distinct_values)
        return {
            distinct_field: distinct_values[distinct_field]
            for distinct_field in self.get_distinct_fields()
        }


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


class LinkedRecordsBase(AbstractBase):
    """Base class for all models that form linked records."""

    _NEXT_NODE_FORMAT = "%(app_label)s_%(class)s_next_node"
    """The name to give the related node of this record."""

    previous_node = models.OneToOneField(
        "self",
        blank=True,
        db_column="previous_node",
        null=True,
        on_delete=models.PROTECT,
        related_name=_NEXT_NODE_FORMAT,
    )

    # By default use pk as the distinct field. This shouldn't really
    # alter the behaviour of linked records and they should behave the
    # same as normal Django records. Subclasses should provide more
    # distinct fields to provide more stronger links.
    objects = LinkedRecordsManager(("pk",))

    model_validators = ["check_not_linked_to_self"]

    @property
    def is_leaf_node(self) -> bool:
        """Return `True` if this is the last node in it's link."""

        return self.next_node is None

    @property
    def is_root_node(self) -> bool:
        """Return `True` if this is the first node in it's link."""

        return getattr(self, "previous_node", None) is None

    @property
    def next_node(self) -> Optional["LinkedRecordsBase"]:
        """Return the next node in the link after this one."""

        next_node_name = self._NEXT_NODE_FORMAT % {
            "app_label": self._meta.app_label,
            "class": self._meta.model_name,
        }
        return getattr(self, next_node_name, None)

    def check_not_linked_to_self(self):
        """Ensure that a node cannot link to itself.

        A node in a linked list can link to other nodes but not itself.
        """
        if self.previous_node and self.previous_node == self:
            raise ValidationError(
                {"previous_node": "An entry must not link to itself."}, code="invalid"
            )

    @transaction.atomic
    def delete(self, *args, **kwargs):
        """Extend the default behaviour to ensure a valid link is maintained after deletion."""

        # Make sure the link is maintained after a deletion.
        prev_node, next_node = self.previous_node, self.next_node
        if next_node:
            nodes = [self, next_node]
            nodes[0].previous_node = None
            nodes[1].previous_node = prev_node
            self._meta.model.objects.bulk_update(nodes, ["previous_node"])
        return super().delete(*args, **kwargs)

    @classmethod
    def leaf_node(cls, **values) -> "LinkedRecordsBase":
        return cls._meta.default_manager.leaf_node(**values)  # type: ignore

    @classmethod
    def leaf_nodes(cls) -> LinkedRecordsQuerySet:
        return cls._meta.default_manager.leaf_nodes()  # type: ignore

    @classmethod
    def nodes(cls, **values) -> LinkedRecordsQuerySet:
        return cls._meta.default_manager.nodes(**values)  # type: ignore

    @classmethod
    def root_node(cls, **values) -> "LinkedRecordsBase":
        return cls._meta.default_manager.root_node(**values)  # type: ignore

    @classmethod
    def root_nodes(cls) -> LinkedRecordsQuerySet:
        return cls._meta.default_manager.root_nodes()  # type: ignore

    class Meta(AbstractBase.Meta):
        abstract = True
