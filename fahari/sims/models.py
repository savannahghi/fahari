from django.db import models
from django.urls import reverse
from django.utils import timezone

from fahari.common.models import AbstractBase, AbstractBaseManager, AbstractBaseQuerySet, Facility

# =============================================================================
# QUERYSETS
# =============================================================================


class QuestionQuerySet(AbstractBaseQuerySet):
    """Queryset for the Question model."""

    def answered_for_questionnaire(
        self, responses: "QuestionnaireResponses"
    ) -> "QuestionQuerySet":
        """Return a queryset containing answered questions for the given questionnaire."""

        return self


class QuestionGroupQuerySet(AbstractBaseQuerySet):
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


class Question(AbstractBase):
    """A question in a questionnaire."""

    class AnswerType(models.TextChoices):
        """The possible types of answer expected for a question."""

        TRUE_FALSE = "true_false", "True/False"
        YES_NO = "yes_no", "Yes/No"
        NUMBER = "number", "Number"
        SHORT_ANSWER = "short_answer", "Short Answer"
        PARAGRAPH = "paragraph", "Long Answer"
        RADIO_OPTION = "radio_option", "Select One"
        SELECT_LIST = "select_list", "Select Multiple"
        DEPENDENT = "dependent", "Depends on Another Answer"
        NONE = "none", "Not Applicable"

    query = models.TextField(verbose_name="Question")
    answer_type = models.CharField(
        max_length=15,
        choices=AnswerType.choices,
        default=AnswerType.SHORT_ANSWER.value,
        help_text="Expected answer type",
    )
    parent = models.ForeignKey(
        "self",
        models.SET_NULL,
        related_name="sub_questions",
        blank=True,
        null=True,
    )
    precedence = models.PositiveIntegerField()
    numbering = models.CharField(max_length=5, default="(i)")
    metadata = models.JSONField(default=dict, blank=True)

    objects = QuestionManager()

    def is_answered_for_questionnaire(self, responses: "QuestionnaireResponses") -> bool:
        """Return true if this question has been answered for the given questionnaire."""

        return self.objects.answered_for_questionnaire(responses).filter(pk=self.pk).exists()

    def __str__(self) -> str:
        return self.query

    def get_absolute_url(self):
        update_url = reverse("ops:question_update", kwargs={"pk": self.pk})
        return update_url


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


class QuestionGroup(AbstractBase):
    """A collection or related questions or nested question question groups."""

    title = models.CharField(max_length=255, verbose_name="Group title")
    questions = models.ManyToManyField(
        Question,
        blank=True,
        related_name="question_groups",
    )
    question_groups = models.ManyToManyField(
        "self", blank=True, related_name="nested_question_groups"
    )
    precedence = models.PositiveIntegerField()
    numbering = models.CharField(max_length=5, default="(a)")

    objects = QuestionGroupManager()

    def is_complete_for_questionnaire(self, responses: "QuestionnaireResponses") -> bool:
        return self.objects.answered_for_questionnaire(responses).filter(pk=self.pk).exists()

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        update_url = reverse("ops:question_group_update", kwargs={"pk": self.pk})
        return update_url

    class Meta(AbstractBase.Meta):
        ordering = ("title",)


class Questionnaire(AbstractBase):
    """A collection of question groups."""

    name = models.CharField(max_length=255)
    question_groups = models.ManyToManyField(QuestionGroup, related_name="questionnaires")

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        update_url = reverse("ops:questionnaire_update", kwargs={"pk": self.pk})
        return update_url

    class Meta(AbstractBase.Meta):
        ordering = ("name",)


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

    def __str__(self) -> str:
        return "Facility: %s, Questionnaire: %s, Status: %s" % (
            self.facility.name,
            self.questionnaire.name,
            "Completed" if self.is_complete else "Draft",
        )
