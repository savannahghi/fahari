from abc import ABCMeta, abstractmethod
from typing import Any, Dict

from django.db import models

# =============================================================================
# CONSTANTS
# =============================================================================

_IS_VALID_ANSWER = models.Q(is_not_applicable=True) | ~models.Q(response__content=None)


# =============================================================================
# ANSWER VALIDITY CHECKERS
# =============================================================================


class AnswerTypeValidityChecker(metaclass=ABCMeta):
    """Represents a utility used to check whether an answer is valid for a given answer type.

    Valid answer types are defined by the `Question.AnswerTypes` enum. This
    interface defines a single method, `self.is_valid_answer_value()` and a
    single property `self.valid_answer_query_expression` that are used to
    check an answer's validity before an answer is saved and after an answer
    is saved respectively.
    """

    @property
    @abstractmethod
    def valid_answer_query_expression(self) -> Any:
        """Return a query expression used to check an answer's validity post save.

        :return: A query expression that can be used to check an answer's validity.
        """
        ...

    @abstractmethod
    def is_valid_answer_value(self, answer_value: Any, is_not_applicable: bool) -> bool:
        """Check an answer's validity before saving.

        Returns `True` if the answer is valid and `False` otherwise.

        :param answer_value: The contents of an answer whose validity is to be checked.
        :param is_not_applicable: Indicates whether the answer is marked as non applicable.

        :return: `True` if the answer is valid and `False` otherwise.
        """
        ...


class FractionAnswerTypeValidityChecker(AnswerTypeValidityChecker):
    """Utility used to check if an answer is valid for fraction answer types."""

    @property
    def valid_answer_query_expression(self) -> Any:
        return models.Q(is_not_applicable=True) | (
            ~models.Q(response__content__0=None) & ~models.Q(response__content__1=None)
        )

    def is_valid_answer_value(self, answer_value: Any, is_not_applicable: bool) -> bool:
        if (
            not is_not_applicable
            and answer_value is not None
            and (type(answer_value) not in (list, tuple) or len(answer_value) != 2)
        ):
            return False
        elif (
            not is_not_applicable
            and answer_value is not None
            and (type(answer_value[0]) is not int or type(answer_value[1]) is not int)
        ):
            return False

        return True


class IntegerAnswerTypeValidityChecker(AnswerTypeValidityChecker):
    """Utility used to check if an answer is valid for integer answer types."""

    @property
    def valid_answer_query_expression(self) -> Any:
        return _IS_VALID_ANSWER

    def is_valid_answer_value(self, answer_value: Any, is_not_applicable: bool) -> bool:
        return is_not_applicable or answer_value is None or type(answer_value) is int


class NoneAnswerTypeValidityChecker(AnswerTypeValidityChecker):
    """Utility used to check if an answer is valid for none answer types."""

    @property
    def valid_answer_query_expression(self) -> Any:
        return models.Q(is_not_applicable=True) | models.Q(response__content=None)

    def is_valid_answer_value(self, answer_value: Any, is_not_applicable: bool) -> bool:
        return answer_value is None


class RealAnswerTypeValidityChecker(AnswerTypeValidityChecker):
    """Utility used to check if an answer is valid for real *(numbers)* answer types."""

    @property
    def valid_answer_query_expression(self) -> Any:
        return _IS_VALID_ANSWER

    def is_valid_answer_value(self, answer_value: Any, is_not_applicable: bool) -> bool:
        return (
            is_not_applicable
            or answer_value is None
            or type(answer_value) is int
            or type(answer_value) is float
        )


class SelectOneAnswerTypeValidityChecker(AnswerTypeValidityChecker):
    """Utility used to check if an answer is valid for select one answer types."""

    @property
    def valid_answer_query_expression(self) -> Any:
        return _IS_VALID_ANSWER

    def is_valid_answer_value(self, answer_value: Any, is_not_applicable: bool) -> bool:
        return True


class SelectMultipleAnswerTypeValidityChecker(AnswerTypeValidityChecker):
    """Utility used to check if an answer is valid for select multiple answer types."""

    @property
    def valid_answer_query_expression(self) -> Any:
        return _IS_VALID_ANSWER

    def is_valid_answer_value(self, answer_value: Any, is_not_applicable: bool) -> bool:
        return (
            is_not_applicable
            or answer_value is None
            or (type(answer_value) in (list, tuple) and answer_value)
        )


class TextAnswerAnswerTypeValidityChecker(AnswerTypeValidityChecker):
    """Utility used to check if an answer is valid for text answer types."""

    @property
    def valid_answer_query_expression(self) -> Any:
        return _IS_VALID_ANSWER

    def is_valid_answer_value(self, answer_value: Any, is_not_applicable: bool) -> bool:
        return bool(
            is_not_applicable
            or answer_value is None
            or (type(answer_value) is str and answer_value)
        )


class YesNoAnswerTypeValidityChecker(AnswerTypeValidityChecker):
    """Utility used to check if an answer is valid for yes no answer types."""

    @property
    def valid_answer_query_expression(self) -> Any:
        return _IS_VALID_ANSWER

    def is_valid_answer_value(self, answer_value: Any, is_not_applicable: bool) -> bool:
        return is_not_applicable or answer_value is None or type(answer_value) is bool


# =============================================================================
# DEFAULT ANSWER TYPE VALIDITY CHECKERS CONFIG
# =============================================================================

DEFAULT_ANSWER_TYPE_VALIDITY_CHECKERS: Dict[str, AnswerTypeValidityChecker] = {
    "FRACTION": FractionAnswerTypeValidityChecker(),
    "INTEGER": IntegerAnswerTypeValidityChecker(),
    "NONE": NoneAnswerTypeValidityChecker(),
    "REAL": RealAnswerTypeValidityChecker(),
    "SELECT_ONE": SelectOneAnswerTypeValidityChecker(),
    "SELECT_MULTIPLE": SelectMultipleAnswerTypeValidityChecker(),
    "TEXT": TextAnswerAnswerTypeValidityChecker(),
    "YES_NO": YesNoAnswerTypeValidityChecker(),
}
