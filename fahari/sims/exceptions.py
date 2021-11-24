from typing import Optional

from .models import Question


class ConstraintCheckError(ValueError):
    ...


class InvalidQuestionMetadataError(ValueError):
    def __init__(
        self,
        metadata_option: str,
        question: Question,  # type: ignore
        error_message: Optional[str] = None,
    ):
        self.metadata_option: str = metadata_option
        self.question = question
        self._error_message = error_message or (
            'Invalid metadata value/configuration for metadata option "%s" on question "%s".'
            % (self.metadata_option, str(self.question))
        )
        super(InvalidQuestionMetadataError, self).__init__(self._error_message)
