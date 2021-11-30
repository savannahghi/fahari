from functools import lru_cache
from numbers import Number
from typing import Any, Dict, List, Literal, Optional, Sequence, TypedDict, Union, cast

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.module_loading import import_string

from fahari.common.models import AbstractBase, AbstractBaseManager, AbstractBaseQuerySet, Facility

# =============================================================================
# CONSTANTS
# =============================================================================

_IS_VALID_ANSWER = models.Q(is_not_applicable=True) | ~models.Q(response__content=None)
"""The expression used to determine if a given answer is valid."""


class MentorshipTeamMemberMetadata(TypedDict):
    """The structure of a mentorship metadata dictionary."""

    name: str
    email: str
    phone: str
    member_org: str
    role: str


class MentorshipQuestionnaireMetadata(TypedDict):
    """The structure of a mentorship questionnaire metadata dictionary."""

    mentors: Sequence[MentorshipTeamMemberMetadata]


class QuestionAnswerResponse(TypedDict):
    """The structure of a question answer response."""

    content: Union[Any, Dict[str, Any], List[Any]]
    """This is the actual content of the answer."""


class QuestionConstraints(TypedDict):
    """The structure of a question's constraints metadata dictionary."""

    comments_required: Optional[bool]
    denominator_max_value: Optional[int]
    denominator_min_value: Optional[int]
    dependency_type: Optional[Literal["denominator", "numerator"]]
    max_length: Optional[Number]
    max_value: Optional[Number]
    min_length: Optional[Number]
    min_value: Optional[Number]
    numerator_max_value: Optional[int]
    numerator_min_value: Optional[int]


class QuestionMetadata(TypedDict):
    """The structure of a question metadata dictionary."""

    constraints: Optional[QuestionConstraints]
    denominator_non_editable: Optional[bool]
    denominator_value: Optional[int]
    depends_on: Optional[str]
    numerator_non_editable: Optional[int]
    numerator_value: Optional[int]
    optional: Optional[bool]
    select_list_options: Optional[Sequence[str]]
    value: Optional[Any]
    value_non_editable: Optional[bool]


# =============================================================================
# HELPERS
# =============================================================================


@lru_cache(maxsize=None)
def get_metadata_processors_for_metadata_option(metadata_option: str) -> Sequence:
    from fahari.sims.question_metadata_processors import QuestionMetadataProcessor

    app_config: Dict[str, Any] = getattr(settings, "SIMS", {})
    _metadata_processors: Dict[str, Sequence[str]] = cast(
        Dict[str, Sequence[str]], app_config.get("QUESTION_METADATA_PROCESSORS", {})
    )
    _option_processors_dotted_paths = _metadata_processors.get(metadata_option, [])

    processors: List[QuestionMetadataProcessor] = []
    for _processor_dotted_path in _option_processors_dotted_paths:
        try:
            processor: QuestionMetadataProcessor = import_string(_processor_dotted_path)()
            processors.append(processor)
        except ImportError as exp:  # pragma: no cover
            raise ImproperlyConfigured(
                "Cannot import question metadata processor from the following dotted path %s"
                % _processor_dotted_path
            ) from exp

    return processors


# =============================================================================
# QUERYSETS
# =============================================================================


class ChildrenMixinQuerySet(models.QuerySet):
    def by_precedence(self) -> models.QuerySet:
        """Return a queryset of elements ordered by precedence."""

        return self.order_by("precedence")

    def parents_only(self) -> models.QuerySet:
        """Return a queryset consisting of only parent elements."""

        return self.alias(  # type: ignore
            parent_pks=self.filter(parent__isnull=False)
            .order_by("parent__pk")
            .values_list("parent", flat=True)
            .distinct("parent")
        ).filter(pk__in=models.F("parent_pks"))


class QuestionQuerySet(AbstractBaseQuerySet["Question"], ChildrenMixinQuerySet):  # noqa
    """Queryset for the Question model."""

    def annotate_with_stats(self, responses: "QuestionnaireResponses") -> "QuestionQuerySet":
        """Annotate each question with use-full stats relating to the given responses.

        The stats added are:
            * stats_is_parent - Indicates whether this is parent question.
            * stats_answer_for_responses_comments
            * stats_answer_for_responses_is_not_applicable
            * stats_answer_for_responses_response

        This method exists as on optimization when rendering a questionnaire
        to reduce the number of queries made to the database when fetching
        for the data contained in the stats.
        """

        return self.annotate(  # type: ignore
            stats_is_parent=models.Exists(Question.objects.filter(parent=models.OuterRef("pk"))),
            stats_answer_for_responses_comments=QuestionAnswer.objects.filter(
                question=models.OuterRef("pk"), questionnaire_response=responses
            ).values("comments"),
            stats_answer_for_responses_is_not_applicable=QuestionAnswer.objects.filter(
                question=models.OuterRef("pk"), questionnaire_response=responses
            ).values("is_not_applicable"),
            stats_answer_for_responses_response=QuestionAnswer.objects.filter(
                question=models.OuterRef("pk"), questionnaire_response=responses
            ).values("response"),
        )

    def answerable(self) -> "QuestionQuerySet":
        """Return a queryset containing questions that accept none "none" answers."""

        return self.exclude(answer_type=Question.AnswerType.NONE.value)

    def answered_for_responses(self, responses: "QuestionnaireResponses") -> "QuestionQuerySet":
        """Return a queryset containing answered questions for the given responses."""

        qs = self.alias(  # type: ignore
            answered_questions_for_questionnaire=responses.answers.filter(  # noqa
                _IS_VALID_ANSWER
            ).values("question")
        ).filter(pk__in=models.F("answered_questions_for_questionnaire"))
        return cast(QuestionQuerySet, qs)

    def for_question(self, question: "Question") -> "QuestionQuerySet":
        """Return all the sub-questions and nested sub-questions belonging to a given question."""

        def visit(questions: "QuestionQuerySet") -> "QuestionQuerySet":
            for _question in questions:
                if _question.is_parent:
                    questions = questions.union(
                        visit(_question.sub_questions.all())  # type: ignore
                    )

            return questions

        return visit(self.filter(parent=question))

    def for_question_group(self, question_group: "QuestionGroup") -> "QuestionQuerySet":
        """Return all the questions belonging to the given question groups.

        This includes all the questions in the nested questions and question groups.
        """

        return self.filter(question_group=question_group)

    def for_questionnaire(self, questionnaire: "Questionnaire") -> "QuestionQuerySet":
        """Return all the questions belonging to the given questionnaire."""

        return self.filter(question_group__questionnaire=questionnaire)


class QuestionGroupQuerySet(AbstractBaseQuerySet["QuestionGroup"], ChildrenMixinQuerySet):  # noqa
    """Queryset for the QuestionGroup model."""

    def annotate_with_stats(self, responses: "QuestionnaireResponses") -> "QuestionGroupQuerySet":
        """Annotate each question group with use-full stats relating to the given responses.

        The stats added are:
            * stats_is_parent - Indicates whether this is parent question group.
            * stats_is_answerable
            * stats_is_complete_for_responses
            * stats_is_not_applicable_for_responses

        This method exists as on optimization when rendering a questionnaire
        to reduce the number of queries made to the database when fetching
        for the data contained in the stats.
        """

        return self.annotate(  # type: ignore
            stats_is_parent=models.Exists(
                QuestionGroup.objects.filter(parent=models.OuterRef("pk"))
            ),
            stats_is_answerable=models.Exists(
                Question.objects.filter(question_group=models.OuterRef("pk"))
            ),
            stats_is_complete_for_responses=~models.Exists(
                Question.objects.filter(question_group=models.OuterRef("pk")).exclude(
                    pk__in=QuestionAnswer.objects.filter(
                        _IS_VALID_ANSWER,
                        question__question_group=models.OuterRef(models.OuterRef("pk")),
                        questionnaire_response=responses,
                    ).values("question")
                )
            ),
            stats_is_not_applicable_for_responses=models.Case(
                models.When(
                    models.Q(stats_is_answerable=True)
                    & models.Q(stats_is_complete_for_responses=True)
                    & ~models.Exists(
                        QuestionAnswer.objects.filter(
                            question__question_group=models.OuterRef("pk"),
                            questionnaire_response=responses,
                        ).exclude(is_not_applicable=True)
                    ),
                    then=models.Value(True),
                ),
                default=models.Value(False),
            ),
        )

    def answered_for_responses(
        self, responses: "QuestionnaireResponses"
    ) -> "QuestionGroupQuerySet":
        """Return a queryset containing answered question groups for the given responses."""

        return self.alias(  # type: ignore
            answered_qg_pks=responses.answers.filter(_IS_VALID_ANSWER)  # noqa
            .order_by("question__question_group__pk")  # noqa
            .values_list("question__question_group", flat=True)
            .distinct("question__question_group")
        ).filter(pk__in=models.F("answered_qg_pks"))

    def for_questionnaire(self, questionnaire: "Questionnaire") -> "QuestionGroupQuerySet":
        """Return a queryset containing all the question groups in the given questionnaire."""

        return self.filter(questionnaire=questionnaire)


class QuestionnaireResponsesQuerySet(AbstractBaseQuerySet["QuestionnaireResponses"]):  # noqa
    """QuerySet for the QuestionnaireResponses model."""

    def draft(self) -> "QuestionnaireResponsesQuerySet":
        """Return a queryset containing responses that have *not* being fully filled."""

        return self._get_by_completion_status().filter(
            models.Q(finish_date__isnull=True) | models.Q(has_incomplete=True)
        )

    def complete(self) -> "QuestionnaireResponsesQuerySet":
        """Return a queryset containing responses that have been fully filled."""

        return self._get_by_completion_status().filter(
            finish_date__isnull=False, has_incomplete=False
        )

    def _get_by_completion_status(self) -> "QuestionnaireResponsesQuerySet":
        """Return a queryset annotated with the current completion status."""

        return self.annotate(  # type: ignore
            has_incomplete=models.Exists(
                Question.objects.filter(
                    question_group__questionnaire=models.OuterRef("questionnaire")
                )
                .exclude(
                    pk__in=QuestionAnswer.objects.filter(
                        question__question_group__questionnaire=models.OuterRef(
                            models.OuterRef("questionnaire")
                        ),
                        questionnaire_response__facility=models.OuterRef(
                            models.OuterRef("facility")
                        ),
                    )
                    .filter(_IS_VALID_ANSWER)
                    .values("question")
                )
                .values("pk")
            )
        )


# =============================================================================
# MANAGERS
# =============================================================================


class QuestionManager(AbstractBaseManager):
    """Manager for the Question model."""

    def annotate_with_stats(self, responses: "QuestionnaireResponses") -> "QuestionQuerySet":
        """Annotate each question with use-full stats relating to the given responses.

        The stats added are:
            * stats_is_parent - Indicates whether this is parent question.
            * stats_answer_for_responses_comments
            * stats_answer_for_responses_is_not_applicable
            * stats_answer_for_responses_response

        This method exists as on optimization when rendering a questionnaire
        to reduce the number of queries made to the database when fetching
        for the data contained in the stats.
        """

        return self.get_queryset().annotate_with_stats(responses)

    def answerable(self) -> "QuestionQuerySet":
        """Return a queryset containing questions that accept none "none" answers."""

        return self.get_queryset().answerable()

    def answered_for_responses(self, responses: "QuestionnaireResponses") -> "QuestionQuerySet":
        """Return a queryset containing answered questions for the given responses."""

        return self.get_queryset().answered_for_responses(responses)

    def by_precedence(self) -> models.QuerySet:
        """Return a queryset of elements ordered by precedence."""

        return self.get_queryset().by_precedence()

    def for_question(self, question: "Question") -> "QuestionQuerySet":
        """Return all the sub-questions and nested sub-questions belonging to a given question."""

        return self.get_queryset().for_question(question)

    def for_question_group(self, question_group: "QuestionGroup") -> "QuestionQuerySet":
        """Return all the questions belonging to the given question groups.

        This includes all the questions in the nested questions and question groups.
        """

        return self.get_queryset().for_question_group(question_group)

    def for_questionnaire(self, questionnaire: "Questionnaire") -> "QuestionQuerySet":
        """Return all the questions belonging to the given questionnaire."""

        return self.get_queryset().for_questionnaire(questionnaire)

    def get_queryset(self) -> QuestionQuerySet:
        return QuestionQuerySet(self.model, using=self.db)


class QuestionGroupManager(AbstractBaseManager):
    """Manager for the QuestionGroup model."""

    def annotate_with_stats(self, responses: "QuestionnaireResponses") -> "QuestionGroupQuerySet":
        """Annotate each question group with use-full stats relating to the given responses.

        The stats added are:
            * stats_is_parent - Indicates whether this is parent question group.
            * stats_is_answerable
            * stats_is_complete_for_responses
            * stats_is_not_applicable_for_responses

        This method exists as on optimization when rendering a questionnaire
        to reduce the number of queries made to the database when fetching
        for the data contained in the stats.
        """

        return self.get_queryset().annotate_with_stats(responses)

    def answered_for_responses(
        self, responses: "QuestionnaireResponses"
    ) -> "QuestionGroupQuerySet":
        """Return a queryset containing answered question groups for the given responses.

        *NB: This will return any question group with answered questions
        for the given responses even if they haven't been fully answered.
        That is, partially answered question groups will also be returned.*
        """

        return self.get_queryset().answered_for_responses(responses)

    def by_precedence(self) -> models.QuerySet:
        """Return a queryset of elements ordered by precedence."""

        return self.get_queryset().by_precedence()

    def for_questionnaire(self, questionnaire: "Questionnaire") -> QuestionGroupQuerySet:
        """Return a queryset containing all the question groups in the given questionnaire."""

        return self.get_queryset().for_questionnaire(questionnaire)

    def get_queryset(self) -> QuestionGroupQuerySet:
        return QuestionGroupQuerySet(self.model, using=self.db)


class QuestionnaireResponsesManager(AbstractBaseManager):
    """Manager for the QuestionnaireResponses model."""

    def draft(self) -> QuestionnaireResponsesQuerySet:
        """Return a queryset containing responses that have not being fully filled."""

        return self.get_queryset().draft()

    def complete(self) -> QuestionnaireResponsesQuerySet:
        """Return a queryset containing responses that have been fully filled."""

        return self.get_queryset().complete()

    def get_queryset(self) -> QuestionnaireResponsesQuerySet:
        return QuestionnaireResponsesQuerySet(self.model, using=self.db)


# =============================================================================
# MODELS
# =============================================================================


class ChildrenMixin(models.Model):
    """Mixin that allows models to contain one to many relations to themselves.

    This effectively allows model instances to contain other instances of the
    same model as children elements.
    """

    class PrecedenceDisplayTypes(models.TextChoices):
        """The available precedence display types."""

        BULLETS = "bullet", "Bullets"
        NUMBERED_TD = "numbered_td", "Numbered with a trailing dot, E.g. 1., 2., 3."
        LOWER_CASE_LETTERS_TCB = (
            "lower_case_letters_tcb",
            "Lower case letter with trailing closing bracket, E.g. a), b), c)",
        )

    parent_field_help_text: Optional[str] = None
    parent_field_related_name: Optional[str] = None
    precedence_display_type_field_help_txt: Optional[str] = None
    precedence_field_help_text: Optional[str] = None

    parent = models.ForeignKey(
        "self",
        models.CASCADE,
        related_name=parent_field_related_name,
        blank=True,
        null=True,
        help_text=cast(str, parent_field_help_text),
    )
    precedence = models.PositiveSmallIntegerField(help_text=cast(str, precedence_field_help_text))
    precedence_display_type = models.CharField(
        max_length=150,
        choices=PrecedenceDisplayTypes.choices,
        null=True,
        blank=True,
        help_text=(
            'The precedence display type of a "container". This sets the '
            "precedence display type for all the child elements of this "
            "container but not the container itself."
        ),
    )

    @property
    def children(self) -> models.QuerySet["ChildrenMixin"]:  # noqa
        """Return all the child elements for whose this instance is the parent."""

        related_field_name: str = self.parent_field_related_name or "parent_set"
        related_query: models.QuerySet[ChildrenMixin] = getattr(self, related_field_name)
        return related_query.all()

    @property
    def is_parent(self) -> bool:
        """Return true if this instance contains child instances."""

        related_field_name: str = self.parent_field_related_name or "parent_set"
        related_query: models.QuerySet = getattr(self, related_field_name)
        return related_query.exists()

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                name="unique_%(app_label)s.%(class)s_precedence_for_parent_container",
                fields=["precedence", "parent"],
                condition=models.Q(parent__isnull=False),
            )
        ]


class Question(AbstractBase, ChildrenMixin):
    """A question in a questionnaire."""

    class AnswerType(models.TextChoices):
        """The possible types of answer expected for a question."""

        DEPENDENT = "dependent", "Dependent on Another Answer"
        FRACTION = "fraction", "Fraction"
        INTEGER = "int", "Whole Number"
        NONE = "none", "Not Applicable"
        REAL = "real", "Real Number"
        SELECT_ONE = "select_one", "Select One"
        SELECT_MULTIPLE = "select_multiple", "Select Multiple"
        TEXT_ANSWER = "text_answer", "Text Answer"
        YES_NO = "yes_no", "Yes/No"

    parent_field_help_text = "The parent question that this question is part of."
    parent_field_related_name = "sub_questions"
    precedence_field_help_text = (
        'The rank of a question within it\'s "container". Used to position '
        "the question when rendering a questionnaire."
    )

    query = models.TextField(verbose_name="Question")
    question_code = models.CharField(
        max_length=100,
        editable=False,
        help_text=(
            "A simple code that can be used to uniquely identify a question. "
            "This is mostly useful in the context of dependent question "
            "answers."
        ),
        unique=True,
    )
    answer_type = models.CharField(
        max_length=15,
        choices=AnswerType.choices,
        default=AnswerType.TEXT_ANSWER.value,
        help_text="Expected answer type",
    )
    question_group = models.ForeignKey(
        "QuestionGroup",
        on_delete=models.CASCADE,
        related_name="questions",
        help_text=(
            "The question group that a question belongs to. Sub-questions "
            "should provide the same group as their parent question."
        ),
    )
    parent = models.ForeignKey(  # type: ignore
        "self",
        models.CASCADE,
        related_name=parent_field_related_name,
        blank=True,
        null=True,
        help_text=parent_field_help_text,
    )
    precedence = models.PositiveSmallIntegerField(help_text=precedence_field_help_text)
    metadata = models.JSONField(default=dict, blank=True)

    objects = QuestionManager()

    @property
    def is_answerable(self) -> bool:
        """Return true if this question accepts non "none" answers."""

        return self.answer_type != self.AnswerType.NONE.value

    def answer_for_responses(
        self, responses: "QuestionnaireResponses"
    ) -> Optional["QuestionAnswer"]:
        """Return the answer to this question from the given questionnaire responses."""

        return responses.answers.filter(question=self).first()  # noqa

    def is_answered_for_responses(self, responses: "QuestionnaireResponses") -> bool:
        """Return true if this question has been answered for the given questionnaire responses.

        If this is a parent question, true will only be returned if all it's
        sub-questions have also being answered.
        """

        if self.is_parent:
            sub_questions: QuestionQuerySet = Question.objects.for_question(self)
            return not sub_questions.difference(
                Question.objects.answered_for_responses(responses)
            ).exists()

        return responses.answers.filter(question=self).exists()  # noqa

    def run_metadata_processors_on_question_save(self) -> None:
        metadata: QuestionMetadata = cast(QuestionMetadata, self.metadata or {})
        for metadata_option in metadata:
            self.run_metadata_option_processors_on_question_save(metadata_option)

    def run_metadata_option_processors_on_question_save(self, metadata_option: str) -> None:
        from fahari.sims.exceptions import InvalidQuestionMetadataError
        from fahari.sims.question_metadata_processors import QuestionMetadataProcessor
        from fahari.sims.question_metadata_processors import (
            QuestionMetadataProcessorRunModes as Qrm,
        )

        processors = get_metadata_processors_for_metadata_option(metadata_option)
        processor: QuestionMetadataProcessor
        for processor in filter(
            lambda p: p.run_mode == Qrm.ON_BOTH or p.run_mode == Qrm.ON_QUESTION_SAVE, processors
        ):
            try:
                processor.process_on_question_save(self)
            except InvalidQuestionMetadataError as exp:  # pragma: no cover
                raise ValidationError({"question": str(exp)}, code="invalid") from exp

    def save(self, *args, **kwargs):
        """Extend the base implementation to also run metadata processors before save."""

        self.run_metadata_processors_on_question_save()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.query

    class Meta(AbstractBase.Meta):
        constraints = [
            *ChildrenMixin.Meta.constraints,
            models.UniqueConstraint(
                name="unique_precedence_for_question_group",
                fields=["precedence", "question_group"],
                condition=models.Q(parent__isnull=True),
            ),
        ]


class QuestionGroup(AbstractBase, ChildrenMixin):
    """A collection or related questions or nested question question groups."""

    parent_field_help_text = "The parent question group that this question group belongs to."
    parent_field_related_name = "sub_question_groups"
    precedence_field_help_text = (
        'The rank of a question group within it\'s "container". Used to '
        "position the question group when rendering a questionnaire."
    )

    title = models.CharField(max_length=255, verbose_name="Group title")
    questionnaire = models.ForeignKey(
        "Questionnaire",
        on_delete=models.CASCADE,
        related_name="question_groups",
        help_text=(
            "The questionnaire that a question group belongs to. Sub-question"
            " groups should provide the same questionnaire as their parent "
            "question group."
        ),
    )
    parent = models.ForeignKey(  # type: ignore
        "self",
        models.CASCADE,
        related_name=parent_field_related_name,
        blank=True,
        null=True,
        help_text=parent_field_help_text,
    )
    precedence = models.PositiveSmallIntegerField(help_text=precedence_field_help_text)

    objects = QuestionGroupManager()

    @property
    def direct_decedents_only(self) -> QuestionQuerySet:
        """Return a queryset of all "parentless" questions belonging to this question group."""

        return self.questions.filter(parent__isnull=True)  # type: ignore

    @property
    def is_answerable(self) -> bool:
        """Return true if this question group has at-least one question."""

        return self.questions.exists()  # noqa

    def is_complete_for_responses(self, responses: "QuestionnaireResponses") -> bool:
        """Return true if this question group has been answered for the given responses."""

        return (
            not Question.objects.for_question_group(self)
            .exclude(
                pk__in=Question.objects.for_question_group(self).answered_for_responses(responses)
            )
            .exists()
        )

    def is_not_applicable_for_responses(self, responses: "QuestionnaireResponses") -> bool:
        """Returns true if this group's questions are not answerable for the given responses.

        That is, for all the questions in this question group, only not
        applicable answers have been provided for the given questionnaire
        responses.
        """

        return (
            self.is_answerable
            and self.is_complete_for_responses(responses)
            and (
                not responses.answers.filter(question__question_group=self)  # noqa
                .exclude(is_not_applicable=True)
                .exists()
            )
        )

    def __str__(self) -> str:
        return self.title

    class Meta(AbstractBase.Meta):
        ordering = ("title",)
        constraints = [
            *ChildrenMixin.Meta.constraints,
            models.UniqueConstraint(
                name="unique_precedence_for_questionnaire",
                fields=["precedence", "questionnaire"],
                condition=models.Q(parent__isnull=True),
            ),
        ]


class Questionnaire(AbstractBase):
    """A collection of question groups."""

    class QuestionnaireTypes(models.TextChoices):
        """The different types of questionnaires."""

        MENTORSHIP = "mentorship", "Mentorship Questionnaire"
        SIMS = "sims", "SIMS Questionnaire"
        OTHER = "other", "Generic Questionnaire"

    name = models.CharField(max_length=255)
    questionnaire_type = models.CharField(
        max_length=15,
        choices=QuestionnaireTypes.choices,
        default=QuestionnaireTypes.MENTORSHIP.value,
    )

    @property
    def direct_decedents_only(self) -> QuestionGroupQuerySet:
        """
        Return a queryset of all "parentless" questions groups belonging to this questionnaire.
        """

        return self.question_groups.filter(parent__isnull=True)  # type: ignore

    def __str__(self) -> str:
        return self.name

    class Meta(AbstractBase.Meta):
        ordering = ("name",)


class QuestionAnswer(AbstractBase):
    """An answer to a question."""

    questionnaire_response = models.ForeignKey(
        "QuestionnaireResponses", on_delete=models.PROTECT, related_name="answers"
    )
    question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name="answers")
    is_not_applicable = models.BooleanField(
        default=False,
        help_text="Indicates that answer is not applicable for the attached question.",
    )
    response = models.JSONField(default=dict)
    answered_on = models.DateTimeField(auto_now=True, editable=False)
    comments = models.TextField(null=True, blank=True)

    @property
    def is_valid(self) -> bool:
        """Return true if this answer is valid for the given question.

        The validity of an answer for a given question is dependent on the
        validation metadata present on a question. Eg. max-length, min-length,
        max_value, min_value, etc.
        """

        # TODO: Add implementation
        return False

    def __str__(self) -> str:
        return "Facility: %s, Question: %s, Response: %s" % (
            self.questionnaire_response.facility.name,
            self.question.query,
            getattr(self, "response", "-"),
        )

    class Meta(AbstractBase.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["question", "questionnaire_response"],
                name="unique_together_question_and_questionnaire_response",
            )
        ]


class QuestionnaireResponses(AbstractBase):
    """Capture the responses to a questionnaire."""

    facility = models.ForeignKey(Facility, on_delete=models.PROTECT)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.PROTECT)
    start_date = models.DateTimeField(default=timezone.now, editable=False)
    finish_date = models.DateTimeField(editable=False, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    objects = QuestionnaireResponsesManager()

    @property
    def answered_questions(self) -> QuestionQuerySet:
        """Return a queryset of all the fully answered questions for this responses."""

        return self.questions.filter(
            pk__in=self.answers.filter(_IS_VALID_ANSWER).values("question")  # noqa
        )

    @property
    def is_complete(self) -> bool:
        """Return True if answerers have been provided for the given questionnaire."""

        return self.finish_date is not None and not (
            Question.objects.for_questionnaire(self.questionnaire)
            .exclude(pk__in=self.answers.filter(_IS_VALID_ANSWER).values("question"))  # noqa
            .exists()
        )

    @property
    def progress(self) -> float:
        """Return the completion status of the given questionnaire as a percentage."""

        total_questions = Question.objects.for_questionnaire(self.questionnaire).count()
        answered_count = self.answers.filter(_IS_VALID_ANSWER).count()  # noqa
        return answered_count / total_questions

    @property
    def questions(self) -> QuestionQuerySet:
        """Return a queryset of the questions being answered for this responses."""

        return Question.objects.for_questionnaire(questionnaire=self.questionnaire)

    def get_absolute_url(self):
        update_url = reverse_lazy("sims:questionnaire_responses_update", kwargs={"pk": self.pk})
        return update_url

    def __str__(self) -> str:
        return "Facility: %s, Questionnaire: %s, Submitted: %s" % (
            self.facility.name,
            self.questionnaire.name,
            str(bool(self.finish_date is not None)),
        )
