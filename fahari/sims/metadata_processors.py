from __future__ import annotations

from abc import ABCMeta
from functools import lru_cache
from itertools import chain
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Sequence, cast

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from fahari.utils.metadata_utils import MetadataEntryProcessor

from .constraints_checkers import ConstraintCheckActivationModes, ConstraintChecker
from .exceptions import (
    ConstraintCheckError,
    QuestionAnswerMetadataProcessingError,
    QuestionMetadataProcessingError,
)

if TYPE_CHECKING:
    from .models import Question, QuestionAnswer, QuestionConstraints, QuestionMetadata

# =============================================================================
# HELPERS
# =============================================================================


@lru_cache(maxsize=None)
def get_registered_constraint_checkers() -> Dict[str, Sequence[ConstraintChecker]]:
    """Returns a dictionary of all registered constraints and constraint checkers.

    This function uses the constraint checkers registered using the
    `SIMS.CONSTRAINT_CHECKER` setting.

    :return: A dictionary of all the registered constraints and constraint
             checkers.
    """

    def dotted_path_to_constraint_checker_instance(dotted_path: str) -> ConstraintChecker:
        try:
            checker: ConstraintChecker = import_string(dotted_path)()
            return checker
        except ImportError as exp:
            raise ImproperlyConfigured(
                "Cannot import constraint checker from the following dotted path %s" % dotted_path
            ) from exp

    app_config: Dict[str, Any] = getattr(settings, "SIMS", {})
    constraint_checkers_config: Dict[str, Sequence[str]] = cast(
        Dict[str, Sequence[str]], app_config.get("CONSTRAINT_CHECKERS", {})
    )
    registered_constraint_checkers: Dict[str, Sequence[ConstraintChecker]] = {}
    for constraint_name, constraint_checkers_paths in constraint_checkers_config.items():
        checkers: Sequence[ConstraintChecker] = tuple(
            map(dotted_path_to_constraint_checker_instance, constraint_checkers_paths)
        )
        registered_constraint_checkers[constraint_name] = checkers

    return registered_constraint_checkers


@lru_cache(maxsize=None)
def get_registered_constraint_checkers_by_activation_mode(
    activation_mode: ConstraintCheckActivationModes,
) -> Dict[str, Sequence[ConstraintChecker]]:
    """Given a constraint checker activation mode, return all applicable constraint checkers.

    This function uses the constraint checkers registered using the
    `SIMS.CONSTRAINT_CHECKER` setting.

    :param activation_mode: The constraint activation mode of the constraint
           checkers of interest.

    :return: A dictionary of all the registered constraints and constraint
             checkers that have the given activation mode.
    """

    all_registered_checkers = get_registered_constraint_checkers()
    checkers_by_activation_mode: Dict[str, Sequence[ConstraintChecker]] = {}
    for constraint_name, constraint_checkers in all_registered_checkers.items():
        c: ConstraintChecker
        checkers: Sequence[ConstraintChecker] = tuple(
            filter(lambda c: c.activation_mode == activation_mode, constraint_checkers)  # noqa
        )
        if checkers:
            checkers_by_activation_mode[constraint_name] = checkers

    return checkers_by_activation_mode


# =============================================================================
# METADATA PROCESSORS
# =============================================================================


class AbstractQuestionAnswerMetadataProcessor(
    MetadataEntryProcessor["QuestionAnswer"], metaclass=ABCMeta
):
    """A skeletal implementation of a `MetadataEntryProcessor` interface.

    This class concrete decedents are meant for use with the `QuestionAnswer`
    metadata container.
    """

    def __init__(self, metadata_entry_name: str, run_on_non_applicable_answers: bool = False):
        self._metadata_entry_name = metadata_entry_name
        self._run_on_non_applicable_answers = run_on_non_applicable_answers

    @property
    def metadata_entry_name(self) -> str:
        return self._metadata_entry_name

    @property
    def run_on_non_applicable_answers(self) -> bool:
        """Indicates whether this entry processor should be run on non-applicable answers."""

        return self._run_on_non_applicable_answers


class AbstractQuestionMetadataProcessor(MetadataEntryProcessor["Question"], metaclass=ABCMeta):
    """A skeletal implementation of a `QuestionMetadataProcessor` interface."""

    def __init__(self, metadata_entry_name: str):
        self._metadata_entry_name = metadata_entry_name

    @property
    def metadata_entry_name(self) -> str:
        return self._metadata_entry_name


class ConstraintsCheckMetadataProcessor(AbstractQuestionAnswerMetadataProcessor):
    """An entry processor that runs constraint checks on a question answer instances."""

    def __init__(self):
        super().__init__("constraints", False)

    def process(
        self, metadata_entry_value: QuestionConstraints, metadata_container: QuestionAnswer
    ) -> None:
        """Given an answer, run checks for the constraints specified in it's associated question.

        An `QuestionAnswerMetadataProcessingError` will be raised for all the
        constraint checks that fail.
        """

        answer_value: Any = self.retrieve_value_from_answer(metadata_container)
        errors: Dict[str, Sequence[str]] = {}
        off_constraint_checkers = get_registered_constraint_checkers_by_activation_mode(
            ConstraintCheckActivationModes.OFF
        )
        on_constraint_checkers = get_registered_constraint_checkers_by_activation_mode(
            ConstraintCheckActivationModes.ON
        )

        # Run constraint checkers with an "ON" activation mode
        self._run_constraint_checkers(
            on_constraint_checkers,
            lambda constraint_name, constraints_meta: constraint_name in constraints_meta,  # noqa
            metadata_entry_value,
            answer_value,
            errors,
        )
        # Run constraint checkers with an "OFF" activation mode
        self._run_constraint_checkers(
            off_constraint_checkers,
            lambda constraint_name, constraints_meta: constraint_name
            not in constraints_meta,  # noqa
            metadata_entry_value,
            answer_value,
            errors,
        )
        if errors:
            error_message = ", ".join(chain.from_iterable(errors.values()))
            raise QuestionAnswerMetadataProcessingError(
                self.metadata_entry_name,
                metadata_entry_value,
                metadata_container,
                answer_value,
                error_message,
                errors,
            )

    def retrieve_value_from_answer(self, answer: QuestionAnswer) -> Any:  # noqa
        """Retrieve the value of an answer from an answer object.

        This implementation assumes the answer response property has a
        content entry that holds the actual value of the answer.
        """
        return answer.response.get("content")

    @staticmethod
    def _run_constraint_checkers(
        constraint_checkers: Dict[str, Sequence[ConstraintChecker]],
        applicability_filter: Callable[[str, QuestionConstraints], bool],
        constraints_meta: QuestionConstraints,
        answer_value: Any,
        errors_dict: Dict[str, Sequence[str]],
    ) -> None:
        """Execute all the provided constraint checkers if they are applicable.

        The `applicability_filter` predicate is used to determine which
        checkers qualify for execution.
        """

        CCMP = ConstraintsCheckMetadataProcessor  # noqa
        for constraint_name, checkers in constraint_checkers.items():
            if not applicability_filter(constraint_name, constraints_meta):
                continue
            constraint_value = constraints_meta.get(constraint_name)  # noqa
            check_errors = CCMP._run_constraint_checkers_for_answer_value(
                checkers, answer_value, constraint_name, constraint_value
            )
            if check_errors:
                constraint_errors: List[str] = list(errors_dict.get(constraint_name, []))
                constraint_errors.extend(check_errors)
                errors_dict[constraint_name] = constraint_errors

    @staticmethod
    def _run_constraint_checkers_for_answer_value(
        constraint_checkers: Sequence[ConstraintChecker],
        answer_value: Any,
        constraint_name: str,
        constraint_value: Any,
    ) -> Sequence[str]:
        """Execute the given constraint checkers for the given answer value."""

        constraint_check_errors: List[str] = []
        for checker in constraint_checkers:
            try:
                checker.check(constraint_name, constraint_value, answer_value)
            except ConstraintCheckError as exp:
                constraint_check_errors.append(str(exp))

        return constraint_check_errors


class DenominatorValueExistIfDenominatorNonEditable(AbstractQuestionMetadataProcessor):
    """
    A metadata processor that ensures that a `denominator_value` metadata
    option has been provided if the `denominator_non_editable` metadata
    option is set on question save.
    """

    def __init__(self):
        super().__init__("denominator_non_editable")

    def process(self, metadata_entry_value: Any, metadata_container: Question) -> None:
        """Ensure that a denominator value has been provided if denominator non editable is set."""

        meta: QuestionMetadata = metadata_container.metadata
        if meta["denominator_non_editable"] is True and meta.get("denominator_value") is None:
            err_message = (
                'The metadata option "denominator_value" must be provided if '
                '"denominator_non_editable" is set.'
            )
            raise QuestionMetadataProcessingError(
                self.metadata_entry_name, metadata_entry_value, metadata_container, err_message
            )


class DependentQuestionExistsMetadataProcessor(AbstractQuestionMetadataProcessor):
    """
    A metadata processor that ensures that the `dependent_on` metadata option
    refers to an existing question on question save.
    """

    def __init__(self):
        super().__init__("depends_on")

    def process(self, metadata_entry_value: Any, metadata_container: Question) -> None:
        """Ensure that the dependent on question does indeed exist."""

        from .models import Question

        try:
            dependent_question_code = metadata_container.metadata["depends_on"]
            Question.objects.get(question_code=dependent_question_code)
        except Question.DoesNotExist:
            err_message = (
                'Question with question_code "%s" does not exist' % dependent_question_code  # noqa
            )
            raise QuestionMetadataProcessingError(
                self.metadata_entry_name, metadata_entry_value, metadata_container, err_message
            )
