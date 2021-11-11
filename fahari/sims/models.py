from typing import Optional, cast

from django.db import models
from django.utils import timezone

from fahari.common.models import AbstractBase, AbstractBaseManager, AbstractBaseQuerySet, Facility

# =============================================================================
# QUERYSETS
# =============================================================================


class ChildrenMixinQuerySet(models.QuerySet):
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

    def answerable(self) -> "QuestionQuerySet":
        """Return a queryset containing questions that accept none "none" answers."""

        return self.exclude(answer_type=Question.AnswerType.NONE.value)

    def answered_for_questionnaire(
        self, responses: "QuestionnaireResponses"
    ) -> "QuestionQuerySet":
        """Return a queryset containing answered questions for the given questionnaire."""

        qs = self.alias(  # type: ignore
            answered_questions_for_questionnaire=QuestionAnswer.objects.filter(
                questionnaire_response=responses
            ).values_list("question", flat=True)
        ).filter(pk__in=models.F("answered_questions_for_questionnaire"))
        return cast(QuestionQuerySet, qs)

    def for_question(self, question: "Question") -> "QuestionQuerySet":
        """Return all the sub-questions and nested sub-questions belonging to a given question."""

        def visit(questions: "QuestionQuerySet") -> "QuestionQuerySet":
            for _question in questions:
                if _question.is_parent:
                    questions = questions.union(visit(_question.sub_questions))  # noqa

            return questions

        return visit(self.filter(parent=question))

    def for_question_group(self, question_group: "QuestionGroup") -> "QuestionQuerySet":
        """Return all the questions belonging to the given question groups.

        This includes all the questions in the nested questions and question groups.
        """

        def visit(question_group: "QuestionGroup") -> "QuestionQuerySet":
            return self

        return question_group.questions.all()

    def for_questionnaire(self, questionnaire: "Questionnaire") -> "QuestionQuerySet":
        """Return all the questions belonging to the given questionnaire."""

        return self


class QuestionGroupQuerySet(AbstractBaseQuerySet, ChildrenMixinQuerySet):
    """Queryset for the QuestionGroup model."""

    def answered_for_questionnaire(
        self, responses: "QuestionnaireResponses"
    ) -> "QuestionGroupQuerySet":
        """Return a queryset containing answered question groups for the given questionnaire."""

        return self


# =============================================================================
# MANAGERS
# =============================================================================


class QuestionManager(AbstractBaseManager):
    """Manager for the Question model."""

    def answered_for_questionnaire(
        self, responses: "QuestionnaireResponses"
    ) -> "QuestionQuerySet":
        """Return a queryset containing answered questions for the given questionnaire."""

        return self.get_queryset().answered_for_questionnaire(responses)

    def get_queryset(self) -> QuestionQuerySet:
        return QuestionQuerySet(self.model, using=self.db)


class QuestionGroupManager(AbstractBaseManager):
    """Manager for the QuestionGroup model."""

    def answered_for_questionnaire(
        self, responses: "QuestionnaireResponses"
    ) -> "QuestionGroupQuerySet":
        """Return a queryset containing answered question groups for the given questionnaire."""

        return self.get_queryset().answered_for_questionnaire(responses)

    def get_queryset(self) -> QuestionGroupQuerySet:
        return QuestionGroupQuerySet(self.model, using=self.db)


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
        models.PROTECT,
        related_name=parent_field_related_name,
        blank=True,
        null=True,
        help_text=parent_field_help_text,
    )
    precedence = models.PositiveSmallIntegerField(help_text=precedence_field_help_text)
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

        TRUE_FALSE = "true_false", "True/False"
        YES_NO = "yes_no", "Yes/No"
        NUMBER = "number", "Whole Number"
        FRACTION = "fraction", "Fractional Number"
        SHORT_ANSWER = "short_answer", "Short Answer"
        PARAGRAPH = "paragraph", "Long Answer"
        RADIO_OPTION = "radio_option", "Select One"
        SELECT_LIST = "select_list", "Select Multiple"
        DEPENDENT = "dependent", "Dependent on Another Answer"
        RATIO = "ratio", "Ratio"
        NONE = "none", "Not Applicable"

    parent_field_help_text = "The parent question that this question is part of."
    parent_field_related_name = "sub_questions"
    precedence_field_help_text = (
        "The rank of a question within it's container. Used to position the "
        "question when rendering a questionnaire."
    )

    query = models.TextField(verbose_name="Question")
    answer_type = models.CharField(
        max_length=15,
        choices=AnswerType.choices,
        default=AnswerType.SHORT_ANSWER.value,
        help_text="Expected answer type",
    )
    question_group = models.ForeignKey(
        "QuestionGroup",
        on_delete=models.PROTECT,
        related_name="questions",
        blank=True,
        null=True,
        help_text=(
            "The question group that a question belongs to. This should "
            "only be provided for questions that are not sub-questions of "
            "other questions."
        ),
    )
    parent = models.ForeignKey(
        "self",
        models.PROTECT,
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

    def is_answered_for_questionnaire(self, responses: "QuestionnaireResponses") -> bool:
        """Return true if this question has been answered for the given questionnaire."""

        if self.is_parent:
            sub_questions: QuestionQuerySet = self.sub_questions  # noqa
            return not sub_questions.difference(
                self.objects.answered_for_questionnaire(responses)
            ).exists()

        return self.objects.answered_for_questionnaire(responses).filter(pk=self.pk).exists()

    def __str__(self) -> str:
        return self.query

    class Meta(AbstractBase.Meta):
        constraints = [
            *ChildrenMixin.Meta.constraints,
            models.UniqueConstraint(
                name="unique_precedence_for_question_group",
                fields=["precedence", "question_group"],
                condition=models.Q(question_group__isnull=False),
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
        on_delete=models.PROTECT,
        related_name="group_questions",
        blank=True,
        null=True,
        help_text=(
            "The questionnaire that a question group belongs to. This should "
            "only be provided for question groups that are not sub-questions "
            "groups of other question groups."
        ),
    )
    parent = models.ForeignKey(
        "self",
        models.PROTECT,
        related_name=parent_field_related_name,
        blank=True,
        null=True,
        help_text=parent_field_help_text,
    )
    precedence = models.PositiveSmallIntegerField(help_text=precedence_field_help_text)

    objects = QuestionGroupManager()

    def is_complete_for_questionnaire(self, responses: "QuestionnaireResponses") -> bool:
        """Return true if this question group has been answered for the given questionnaire."""

        return self.objects.answered_for_questionnaire(responses).filter(pk=self.pk).exists()

    def __str__(self) -> str:
        return self.title

    class Meta(AbstractBase.Meta):
        ordering = ("title",)
        constraints = [
            *ChildrenMixin.Meta.constraints,
            models.UniqueConstraint(
                name="unique_precedence_for_questionnaire",
                fields=["precedence", "questionnaire"],
                condition=models.Q(questionnaire__isnull=False),
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
    response = models.JSONField(default=dict)
    answered_on = models.DateTimeField(default=timezone.datetime.now)
    comments = models.TextField(null=True, blank=True)

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

    @property
    def is_complete(self) -> bool:
        """Return True if answerers have been provided for the given questionnaire."""

        return False

    @property
    def progress(self) -> float:
        """Return the completion status of the given questionnaire as a percentage."""

        return 0.0

    def __str__(self) -> str:
        return "Facility: %s, Questionnaire: %s, Status: %s" % (
            self.facility.name,
            self.questionnaire.name,
            "Completed" if self.is_complete else "Draft",
        )
