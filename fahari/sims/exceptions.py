from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from fahari.utils.metadata_utils import MetadataEntryProcessingError

if TYPE_CHECKING:
    from .models import Question, QuestionAnswer


class ConstraintCheckError(RuntimeError):
    """An exception raised when a constrain check fails."""

    def __init__(
        self,
        constraint_name: str,
        constraint_value: Any,
        answer_value: Any,
        error_message: Optional[str] = None,
    ):
        self.constraint_name: str = constraint_name
        self.constraint_value: Any = constraint_value
        self.answer_value: Any = answer_value
        self._error_message = error_message or (
            'The value "%s" breaks the constraint "%s" with constraint value "%s".'
            % (str(self.answer_value), self.constraint_name, str(self.constraint_value))
        )
        super(ConstraintCheckError, self).__init__(self._error_message)


class QuestionAnswerMetadataProcessingError(MetadataEntryProcessingError):
    """An exception raised when a metadata entry processor run on an answer fails.

    This is appropriate to raise in case of an invalid metadata configuration
    or in case of an invalid metadata value.
    """

    def __init__(
        self,
        metadata_entry_name: str,
        metadata_entry_value: Any,
        answer: QuestionAnswer,
        answer_value: Any,
        error_message: Optional[str] = None,
        *args
    ):
        self.answer: QuestionAnswer = answer
        self.answer_value: Any = answer_value
        self._error_message = error_message or (
            "Invalid metadata value/configuration for metadata option "
            '"%s" on an answer of question "%s" and value "%s".'
            % (metadata_entry_name, str(self.answer.question), str(self.answer_value))
        )
        super().__init__(metadata_entry_name, metadata_entry_value, self._error_message, *args)


class QuestionMetadataProcessingError(MetadataEntryProcessingError):
    """An exception raised when a metadata entry processor running on question save fails.

    This is appropriate to raise in case of an invalid metadata configuration
    or in case of an invalid metadata value.
    """

    def __init__(
        self,
        metadata_entry_name: str,
        metadata_entry_value: Any,
        question: Question,
        error_message: Optional[str] = None,
        *args
    ):
        self.question: Question = question
        self._error_message = error_message or (
            'Invalid metadata value/configuration for metadata option "%s" on question "%s".'
            % (metadata_entry_name, str(self.question))
        )
        super().__init__(metadata_entry_name, metadata_entry_value, self._error_message, *args)
