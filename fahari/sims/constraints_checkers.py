"""
The module is intended to work with the values
"""
from abc import ABCMeta, abstractmethod
from enum import IntEnum
from numbers import Number
from typing import Any, Generic, Optional, Sequence, TypeVar

from .exceptions import ConstraintCheckError

C = TypeVar("C")
V = TypeVar("V")


class ConstraintCheckActivationModes(IntEnum):
    """The two possible validator activation modes are either on or off.

    `On` means the checker is activated once a constraint is encountered
    inside a questions metadata. `Off` means the checker is activated if
    a constraint is missing from a questions metadata. The off mode is
    useful for specifying default validations. E.g. Specifying that an
    answer value is required by default.
    """

    OFF = 0
    ON = 1


class ConstraintChecker(Generic[C, V], metaclass=ABCMeta):
    """This class describes the interface of a constraint checker."""

    @property
    @abstractmethod
    def activation_mode(self) -> ConstraintCheckActivationModes:
        ...

    @abstractmethod
    def check(self, constraint_name: str, constraint_value: C, value: Optional[V]) -> None:
        ...


class AbstractConstraintChecker(Generic[C, V], ConstraintChecker[C, V]):
    """A skeletal implementation of the `ConstraintChecker` interface."""

    def __init__(self, activation_mode: ConstraintCheckActivationModes):
        self._activation_mode: ConstraintCheckActivationModes = activation_mode

    @property
    def activation_mode(self) -> ConstraintCheckActivationModes:
        return self._activation_mode

    @abstractmethod
    def check(self, constraint_name: str, constraint_value: C, value: Optional[V]) -> None:
        ...


class MaxValueConstraintChecker(AbstractConstraintChecker[Number, Number]):
    """A constraint checker that ensures that a number is not greater than a given threshold."""

    def __init__(self):
        super().__init__(ConstraintCheckActivationModes.ON)

    def check(
        self, constraint_name: str, constraint_value: Number, value: Optional[Number]
    ) -> None:
        if value > constraint_value:  # type: ignore
            raise ConstraintCheckError(
                constraint_name,
                constraint_value,
                value,
                "The given number must not exceed %s." % str(constraint_value),
            )


class MinValueConstraintChecker(AbstractConstraintChecker[Number, Number]):
    """A constraint check that ensures that a number is not smaller than a given minimum."""

    def __init__(self):
        super().__init__(ConstraintCheckActivationModes.ON)

    def check(
        self, constraint_name: str, constraint_value: Number, value: Optional[Number]
    ) -> None:
        if value < constraint_value:  # type: ignore
            raise ConstraintCheckError(
                constraint_name,
                constraint_value,
                value,
                "The given number must not be lesser than %s." % str(constraint_value),
            )


class NumeratorMaxValueConstraintChecker(AbstractConstraintChecker[int, Sequence[int]]):
    """A constraint check to ensure that a numerator doesn't exceed a given threshold."""

    def __init__(self):
        super().__init__(ConstraintCheckActivationModes.ON)

    def check(
        self,
        constraint_name: str,
        constraint_value: int,
        value: Optional[Sequence[int]],
    ) -> None:
        if value and value[0] > constraint_value:
            raise ConstraintCheckError(
                constraint_name,
                constraint_value,
                value[0],
                "The numerator must not be greater than %s." % str(constraint_value),
            )


class RequiredByDefaultConstraintChecker(AbstractConstraintChecker[None, Any]):
    """A constraint checker to ensure that a value is provided by default.

    This checker is only run if the `optional` constraint has not been
    provided which this checker assumes to mean that the value is required.
    """

    def __init__(self):
        super().__init__(ConstraintCheckActivationModes.OFF)

    def check(self, constraint_name: str, constraint_value: None, value: Any) -> None:
        if value is None or value == "":
            raise ConstraintCheckError(
                constraint_name, constraint_value, value, "This value must be provided."
            )
