from django.contrib import admin

from fahari.common.admin import BaseAdmin

from .models import Question, QuestionAnswer, QuestionGroup, Questionnaire, QuestionnaireResponses


@admin.register(Question)
class QuestionAdmin(BaseAdmin):
    ...


@admin.register(Questionnaire)
class QuestionnaireAdmin(BaseAdmin):
    ...


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(BaseAdmin):
    ...


@admin.register(QuestionGroup)
class QuestionGroupAdmin(BaseAdmin):
    ...


@admin.register(QuestionnaireResponses)
class QuestionnaireResponsesAdmin(BaseAdmin):
    ...
