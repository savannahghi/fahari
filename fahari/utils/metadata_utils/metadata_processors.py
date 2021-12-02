from abc import ABCMeta, abstractmethod
from functools import lru_cache
from typing import Any, Dict, Generic, Mapping, Sequence, TypeVar

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

# =============================================================================
# CONSTANTS
# =============================================================================

HM = TypeVar("HM")  # Has Metadata
"""An object that has metadata."""

Metadata = Mapping[str, Any]


# =============================================================================
# HELPERS
# =============================================================================


@lru_cache(maxsize=None)
def _load_all_processors() -> Mapping[str, Sequence["MetadataEntryProcessor"]]:
    """Helper that loads and returns all registered processors."""

    def map_entry_processor_path_to_instance(entry_processor_path: str) -> MetadataEntryProcessor:
        try:
            instance: MetadataEntryProcessor = import_string(entry_processor_path)()
            return instance
        except ImportError as exp:
            raise ImproperlyConfigured(
                "Cannot import question metadata processor from the following dotted path %s"
                % entry_processor_path
            ) from exp

    registered_processors: Mapping[str, Sequence[str]] = getattr(
        settings, "METADATA_PROCESSORS", {}
    )
    loaded_processors: Dict[str, Sequence[MetadataEntryProcessor]] = {}
    for metadata_processor, entry_processors_paths in registered_processors.items():
        loaded_processors[metadata_processor] = tuple(
            map(map_entry_processor_path_to_instance, entry_processors_paths)
        )

    return loaded_processors


@lru_cache(maxsize=None)
def get_registered_metadata_entry_processors(
    metadata_entry_name: str, metadata_processor_qualified_class_name: str
) -> Sequence["MetadataEntryProcessor"]:
    """
    Return all applicable processors for the given metadata entry name and
    metadata processor identifier.

    This function uses the metadata processors registered using the
    `METADATA_PROCESSORS` django setting. If no matching metadata processors
    for the given metadata entry name and metadata identifier are found,
    then an empty sequence is returned instead.

    :param metadata_entry_name: The name of the metadata entry processor whose
           (metadata entry)processors are to be returned.
    :param metadata_processor_qualified_class_name: A unique identifier used
           to register and identifier a metadata processor.

    :return: A sequence of matching metadata processors or an empty sequence
             if no matching metadata processors exists.
    """

    processors: Sequence[MetadataEntryProcessor] = _load_all_processors().get(
        metadata_processor_qualified_class_name, tuple()
    )
    return tuple(filter(lambda p: p.metadata_entry_name == metadata_entry_name, processors))


# =============================================================================
# METADATA PROCESSOR INTERFACE
# =============================================================================


class MetadataProcessor:
    """This class describes the interface for classes that support metadata processing.
    It contains methods for retrieving the metadata from a metadata container
    and running the registered metadata entry's processors.

    *Note: Although this class would be a good candidate for having ABCMeta
    as it's metaclass, it is implemented as a non-ABC so that it can be used
    as a base class by Django models.*
    """

    def get_metadata(self) -> Metadata:
        """Return the metadata entries to use during processing.

        :return: A mapping that contains metadata entries.
        """

        raise NotImplementedError("`get_metadata` must be implemented.")

    def get_qualified_class_name(self) -> str:
        """Return the fully qualified name of this metadata processor.

        :return: A fully qualified name for this metadata processor.
        """

        return "%s.%s" % (self.__module__, self.__class__.__qualname__)

    def run(self) -> None:
        """Run all metadata entries processors."""

        metadata = self.get_metadata()
        for metadata_entry_name in metadata:
            self.run_metadata_entry_processors_for_entry(metadata_entry_name)

    def run_metadata_entry_processors_for_entry(self, metadata_entry_name: str) -> None:
        """Run metadata processors for the given entry."""

        processors = get_registered_metadata_entry_processors(
            metadata_entry_name, self.get_qualified_class_name()
        )
        processor: MetadataEntryProcessor
        for processor in processors:
            self.run_metadata_entry_processor(processor)

    def run_metadata_entry_processor(self, processor: "MetadataEntryProcessor") -> None:
        """Run the given metadata entry processor."""

        raise NotImplementedError("`run_processor` must be implemented.")


# =============================================================================
# METADATA ENTRY PROCESSOR INTERFACE
# =============================================================================


class MetadataEntryProcessor(Generic[HM], metaclass=ABCMeta):
    """This class describes the interface of a metadata entry processor."""

    @property
    @abstractmethod
    def metadata_entry_name(self) -> str:
        ...

    @abstractmethod
    def process(self, metadata_entry_value: Any, metadata_container: HM) -> None:
        ...
