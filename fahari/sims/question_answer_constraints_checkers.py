"""
The module is intended to work with the values
"""
from abc import ABCMeta, abstractmethod
from enum import IntEnum
from numbers import Number
from typing import Generic, Optional, TypeVar

C = TypeVar("C")
V = TypeVar("V")


class ConstraintCheckActivationModes(IntEnum):
    """The two possible validator activation modes are either on or off.

    `On` means the validator is activated once a constraint is encountered
    inside a questions metadata. `Off` means the opposite.
    """

    OFF = 0
    ON = 1


class ConstraintChecker(Generic[C, V], metaclass=ABCMeta):
    @property
    @abstractmethod
    def activation_mode(self) -> ConstraintCheckActivationModes:
        ...

    @abstractmethod
    def check(self, constraint_value: C, value: Optional[V]) -> None:
        ...


class AbstractConstraintChecker(Generic[C, V], ConstraintChecker[C, V]):
    def __init__(self, activation_mode: ConstraintCheckActivationModes):
        self._activation_mode: ConstraintCheckActivationModes = activation_mode

    @property
    def activation_mode(self) -> ConstraintCheckActivationModes:
        return self._activation_mode

    @abstractmethod
    def check(self, constraint_value: C, value: Optional[V]) -> None:
        ...


class MaxValueConstraintChecker(AbstractConstraintChecker[Number, Number]):
    def __init__(self):
        super().__init__(ConstraintCheckActivationModes.ON)

    def check(self, constraint_value: Number, value: Optional[Number]) -> None:
        if value is not None and value > constraint_value:  # type: ignore
            raise ValueError


class MinValueConstraintChecker(AbstractConstraintChecker[Number, Number]):
    def __init__(self):
        super().__init__(ConstraintCheckActivationModes.ON)

    def check(self, constraint_value: Number, value: Optional[Number]) -> None:
        if value is not None and value < constraint_value:  # type: ignore
            raise ValueError
