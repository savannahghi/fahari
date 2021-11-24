from abc import ABCMeta, abstractmethod
from enum import IntEnum

from .exceptions import InvalidQuestionMetadataError
from .models import Question, QuestionAnswer


class QuestionMetadataProcessorRunModes(IntEnum):
    """
    Specifies when question metadata processors should be run.
    """

    ON_BOTH = 0
    ON_QUESTION_ANSWER_SAVE = 1
    ON_QUESTION_SAVE = 2


class QuestionMetadataProcessor(metaclass=ABCMeta):
    @property
    @abstractmethod
    def run_mode(self) -> QuestionMetadataProcessorRunModes:
        ...

    @abstractmethod
    def process_on_answer_save(self, answer: QuestionAnswer) -> None:
        ...

    @abstractmethod
    def process_on_question_save(self, question: Question) -> None:
        ...


class AbstractDependsOnQuestionMetadataProcessor(QuestionMetadataProcessor):
    def __init__(self, run_mode: QuestionMetadataProcessorRunModes, metadata_option: str):
        self._run_mode: QuestionMetadataProcessorRunModes = run_mode
        self._metadata_option = metadata_option

    @property
    def metadata_option(self) -> str:
        return self._metadata_option

    @property
    def run_mode(self) -> QuestionMetadataProcessorRunModes:
        return self._run_mode

    @abstractmethod
    def process_on_answer_save(self, answer: QuestionAnswer) -> None:
        ...

    @abstractmethod
    def process_on_question_save(self, question: Question) -> None:
        ...


class ConstraintsQuestionMetadataProcessor(AbstractDependsOnQuestionMetadataProcessor):
    def __init__(self):
        super(ConstraintsQuestionMetadataProcessor, self).__init__(
            QuestionMetadataProcessorRunModes.ON_QUESTION_ANSWER_SAVE, "constraints"
        )

    def process_on_answer_save(self, answer: QuestionAnswer) -> None:
        ...

    def process_on_question_save(self, question: Question) -> None:
        ...


class DependsOnQuestionMetadataProcessor(AbstractDependsOnQuestionMetadataProcessor):
    def __init__(self):
        super(DependsOnQuestionMetadataProcessor, self).__init__(
            QuestionMetadataProcessorRunModes.ON_QUESTION_SAVE, "depends_on"
        )

    def process_on_answer_save(self, answer: QuestionAnswer) -> None:
        ...

    def process_on_question_save(self, question: Question) -> None:
        """Ensure that the dependent on question does indeed exist."""

        from fahari.sims.models import Question

        try:
            dependent_question_code = question.metadata["depends_on"]
            Question.objects.get(question_code=dependent_question_code)
        except Question.DoesNotExist:
            err_message = (
                'Question with question_code "%s" does not exist' % dependent_question_code  # noqa
            )
            raise InvalidQuestionMetadataError(self.metadata_option, question, err_message)
