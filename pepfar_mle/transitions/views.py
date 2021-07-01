from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.serializers import ValidationError


class TransitionViewMixin(object):
    def __init__(self, *args, **kwargs):
        assert isinstance(self, UpdateModelMixin), (
            "TransitionViewMixin works with " "UpdateAPIView or RetriveUpdateAPIView"
        )
        super(TransitionViewMixin, self).__init__(*args, **kwargs)

    def process_data(
        self, data, transition_from, transition_to, *args, **kwargs
    ):  # noqa
        """
        Override this method to handle data.
        :param data dict Read only dict data structure containing data posted.
        :param transition_from string Previous state
        :param transition_to string Next state
        """
        pass

    def get_transition(self, request, *args, **kwargs):
        return kwargs.pop(self.transition_field, "").upper()

    def update(self, request, *args, **kwargs):
        """Override this to call super().update() if the desired
        effect is not to have update map to transition logic.
        """
        return self.transition(request, *args, **kwargs)

    def transition(self, request, *args, **kwargs):
        """
        For the instance transition field will be saved in this view. Any other
        field is being ignored
        """
        assert self.transition_field, "Transition field has not been set"
        # make instance accessible at class object level
        self.instance = self.get_object()
        assert hasattr(
            self.instance, self.transition_field
        ), "Target object has no attribute {}".format(self.transition_field)

        _from = getattr(self.instance, self.transition_field)

        _to = self.get_transition(request, *args, **kwargs)

        data = request.data

        setattr(self.instance, self.transition_field, _to)
        try:
            with transaction.atomic():
                self.process_data(data, _from, _to, *args, **kwargs)
                ret = self.instance.transition(data)
                serializer = self.get_serializer(ret)
                return Response(serializer.data, status=200)
        except DjangoValidationError as e:
            error = e.message_dict if hasattr(e, "message_dict") else e.messages
            raise ValidationError(error)

    def _save(self, payload, serializer_class, many=False):
        kwargs = {"context": self.get_serializer_context()}
        serializer = serializer_class(data=payload, many=many, **kwargs)
        serializer.is_valid(raise_exception=True)
        serializer.save()
