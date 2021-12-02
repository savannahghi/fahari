from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Generic, List, TypeVar, Union

from django.core.exceptions import ValidationError

# =============================================================================
# CONSTANTS
# =============================================================================

P = TypeVar("P")
R = TypeVar("R")


# =============================================================================
# CONSTANTS
# =============================================================================


def _ensure_answer_value_is_provided(answer_value: Any, message: str = None) -> None:
    if answer_value is None or answer_value == "":
        raise ValidationError(message or "Please provide an answer.")


# =============================================================================
# ANSWER VALUE CONVERTORS
# =============================================================================


class AnswerValueConvertor(Generic[P, R], metaclass=ABCMeta):
    @abstractmethod
    def to_python(self, representation_value: R) -> P:
        ...

    @abstractmethod
    def to_representation(self, python_value: P) -> R:
        ...


class FractionAnswerValueConvertor(AnswerValueConvertor[List[int], List[str]]):
    def to_python(self, representation_value: List[str]) -> List[int]:
        _ensure_answer_value_is_provided(representation_value)
        if type(representation_value) not in (list, tuple) or len(representation_value) != 2:
            raise ValidationError("Invalid answer.")
        _ensure_answer_value_is_provided(representation_value[0], "Please provide the numerator.")
        _ensure_answer_value_is_provided(
            representation_value[1], "Please provide the denominator."
        )

        try:
            int(representation_value[0])
        except ValueError:
            raise ValidationError("The numerator must be a valid integer.")

        try:
            int(representation_value[1])
        except ValueError:
            raise ValidationError("The denominator must be a valid integer.")

        return [int(representation_value[0]), int(representation_value[1])]

    def to_representation(self, python_value: List[int]) -> List[str]:
        raise NotImplementedError(
            '"FractionAnswerValueConvertor.to_representation" must be implemented.'
        )


class IntegerAnswerValueConvertor(AnswerValueConvertor[int, Union[int, str]]):
    def to_python(self, representation_value: Union[int, str]) -> int:
        _ensure_answer_value_is_provided(representation_value)
        try:
            return int(representation_value)
        except ValueError:
            raise ValidationError('"%s" is not a valid integer.' % str(representation_value))

    def to_representation(self, python_value: int) -> Union[int, str]:
        raise NotImplementedError(
            '"IntegerAnswerValueConvertor.to_representation" must be implemented.'
        )


class NoneAnswerValueConvertor(AnswerValueConvertor[None, Any]):
    def to_python(self, representation_value: Any) -> None:
        return None

    def to_representation(self, python_value: None) -> Any:
        raise NotImplementedError(
            '"NoneAnswerValueConvertor.to_representation" must be implemented.'
        )


class RealAnswerValueConvertor(AnswerValueConvertor[float, Union[float, str]]):
    def to_python(self, representation_value: Union[float, str]) -> float:
        _ensure_answer_value_is_provided(representation_value)
        try:
            return float(representation_value)
        except ValueError:
            raise ValidationError('"%s" is not a valid float number.' % str(representation_value))

    def to_representation(self, python_value: float) -> Union[float, str]:
        raise NotImplementedError(
            '"RealAnswerValueConvertor.to_representation" must be implemented.'
        )


class SelectOneAnswerValueConvertor(AnswerValueConvertor[str, str]):
    def to_python(self, representation_value: str) -> str:
        _ensure_answer_value_is_provided(representation_value)
        return representation_value

    def to_representation(self, python_value: str) -> str:
        raise NotImplementedError(
            '"SelectOneAnswerValueConvertor.to_representation" must be implemented.'
        )


class SelectMultipleAnswerValueConvertor(AnswerValueConvertor[List[str], List[str]]):
    def to_python(self, representation_value: List[str]) -> List[str]:
        _ensure_answer_value_is_provided(representation_value)
        return representation_value

    def to_representation(self, python_value: List[str]) -> List[str]:
        raise NotImplementedError(
            '"SelectMultipleAnswerValueConvertor.to_representation" must be implemented.'
        )


class TextAnswerValueConvertor(AnswerValueConvertor[str, str]):
    def to_python(self, representation_value: str) -> str:
        _ensure_answer_value_is_provided(representation_value)
        return representation_value

    def to_representation(self, python_value: str) -> str:
        raise NotImplementedError(
            '"TextAnswerValueConvertor.to_representation" must be implemented.'
        )


class YesNoAnswerValueConvertor(AnswerValueConvertor[bool, str]):
    def to_python(self, representation_value: str) -> bool:
        _ensure_answer_value_is_provided(representation_value)
        if representation_value not in ("false", "true"):
            raise ValidationError(
                'invalid value "%s". Valid values are "true" or "false".'
                % str(representation_value)
            )
        return representation_value == "true"

    def to_representation(self, python_value: bool) -> str:
        raise NotImplementedError(
            '"YesNoAnswerValueConvertor.to_representation" must be implemented.'
        )


# =============================================================================
# DEFAULT ANSWER VALUE CONVERTORS
# =============================================================================

DEFAULT_ANSWER_VALUE_CONVERTERS: Dict[str, AnswerValueConvertor] = {
    "fraction": FractionAnswerValueConvertor(),
    "int": IntegerAnswerValueConvertor(),
    "none": NoneAnswerValueConvertor(),
    "real": RealAnswerValueConvertor(),
    "select_one": SelectOneAnswerValueConvertor(),
    "select_multiple": SelectMultipleAnswerValueConvertor(),
    "text": TextAnswerValueConvertor(),
    "yes_no": YesNoAnswerValueConvertor(),
}
