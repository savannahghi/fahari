from rest_framework import serializers

from fahari.common.serializers import BaseSerializer, FacilitySerializer

from .models import QuestionAnswer, QuestionGroup, Questionnaire, QuestionnaireResponses


class QuestionAnswerSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = QuestionAnswer
        fields = "__all__"


class QuestionGroupSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = QuestionGroup
        fields = "__all__"


class QuestionnaireSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Questionnaire
        fields = "__all__"


class QuestionnaireResponsesSerializer(BaseSerializer):

    facility_data = FacilitySerializer(source="facility", read_only=True)
    questionnaire_data = QuestionnaireSerializer(source="questionnaire", read_only=True)
    is_complete = serializers.BooleanField(read_only=True)
    progress = serializers.FloatField(read_only=True)
    start_date = serializers.DateTimeField(format="%d %b %Y, %I:%M:%S %p", read_only=True)
    finish_date = serializers.DateTimeField(format="%d %b %Y, %I:%M:%S %p", read_only=True)

    class Meta(BaseSerializer.Meta):
        model = QuestionnaireResponses
        fields = "__all__"
