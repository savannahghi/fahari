from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from .utils import SkipTransitionException, is_valid_transition


class TransitionMixinsBase(object):
    def __init__(self, *args, **kwargs):
        super(TransitionMixinsBase, self).__init__(*args, **kwargs)

        # Check field to be logged
        assert self._transition_field, "Transition field has not been set"
        assert self._transition_field in [
            f.name for f in self._meta.fields
        ], "Target object has no attribute {}".format(self._transition_field)

        fields = self.get_deferred_fields()
        if self._transition_field in fields:
            self._old_transition_value = None
            return

        self._old_transition_value = (
            getattr(self, self._transition_field)
            if hasattr(self, self._transition_field)
            else None
        )

    def get_transition_graph(self):
        """This method allows for returning of a custom transition graph"""
        return self._transition_graph

    def can_transition_to(self, _from, _to):
        transition_graph = self.get_transition_graph()
        return is_valid_transition(transition_graph, _from, _to)


class TransitionLogMixin(TransitionMixinsBase):
    """
    Model mixin which logs changes of a specified field in the specified
    model. The log model should have a *field*_from and *field*_to fields as
    well as a relevant fk field for what is being logged
    """

    def __init__(self, *args, **kwargs):
        super(TransitionLogMixin, self).__init__(*args, **kwargs)

        # Check whether log model is specified
        assert self._transition_log_model, "Transition log model has not been set"
        # Check that the name of the field exists in the transition log model
        assert (
            self._transition_log_model_fk_field
        ), "Transition Log model field name has not been set"
        assert hasattr(
            self._transition_log_model, self._transition_log_model_fk_field
        ), "Target log object has no attribute {}".format(
            self._transition_log_model_fk_field
        )

    def transition_log_data(self):
        """
        Provide the data to create the log.

        Can be overriden to provide different data or to append
        extra data.
        """
        from_field = str(self._transition_field) + "_from"
        to_field = str(self._transition_field) + "_to"
        data = {
            from_field: self._old_transition_value,
            to_field: self._new_transition_value,
            str(self._transition_log_model_fk_field): self,
        }
        return data

    def run_transition_validations(self):
        pass

    def create_transition_log(self):
        data = self.transition_log_data()
        log_kwargs = getattr(self, "_transition_log_kwargs", {})
        data.update(log_kwargs)
        self._transition_log_model._default_manager.create(**data)

    @transaction.atomic
    def save(self, *args, **kwargs):
        created = not self.__class__._default_manager.filter(pk=self.pk).exists()
        self._new_transition_value = getattr(self, self._transition_field)
        self.run_transition_validations()
        super(TransitionLogMixin, self).save(*args, **kwargs)

        LOG_TRANSITION = getattr(settings, "LOG_TRANSITION", True)

        if not created and LOG_TRANSITION:
            # Check that the transition field has changed and create log
            if self._old_transition_value != self._new_transition_value:
                self.create_transition_log()

        _to = getattr(self, self._transition_field)
        self._old_transition_value = _to

        return self


class TransitionMixin(TransitionMixinsBase):

    SkipTransitionException = SkipTransitionException

    _transition_graph = None

    def __init__(self, *args, **kwargs):
        super(TransitionMixin, self).__init__(*args, **kwargs)
        assert self._transition_graph or self.get_transition_graph(), (
            "Transition graph has not been specified. Assign class attribute"
            "_transition_graph or define method get_transition_graph."
        )

    def process_transition(self, data, transition_from, transition_to):
        """
        Override this method to implement the cascading effect of a transition.

        Args:
        :param data dict Read only dict data structure containing data posted.
        :param transition_from (string) Previous workflow state
        :param transition_to string Next workflow state
        """

    def post_transition(self, data, transition_from, transition_to):
        """Override this method to add functionality to follow a transition.

        Args:
        :param data dict Data passed on to the transition method for futher
            processing
        :param transition_from (string) Previous workflow state
        :param transition_to string Next workflow state
        """

    def pre_transition(self, data, transition_from, transition_to):
        """Override this method to add functionality to precede a transition.

        Args:
        :param data dict Data passed on to the transition method for
            processing
        :param transition_from (string) Previous workflow state
        :param transition_to string Next workflow state
        """

    @transaction.atomic
    def transition(self, data):
        """
        Model instance method responsible for handling transitions.
        """
        _from = self._old_transition_value

        _to = getattr(self, self._transition_field)

        if self.can_transition_to(_from, _to):
            try:
                self.pre_transition(data, _from, _to)
                self.process_transition(data, _from, _to)
                self.save()
                self._old_transition_value = _to
                self.post_transition(data, _from, _to)
            except SkipTransitionException:
                return self
        else:
            error = {
                self._transition_field: "{} to {}"
                " is an invalid transition.".format(_from, _to)
            }
            raise ValidationError(error)
        return self


class TransitionAndLogMixin(TransitionMixin, TransitionLogMixin):
    pass
