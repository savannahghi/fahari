import copy

from django.core.exceptions import ValidationError


class SkipTransitionException(Exception):
    pass


def expand_list(nested):
    """
    Return nested lists as one list
    """
    ret = []
    for each in nested:
        if isinstance(each, list):
            ret.extend(expand_list(each))
        else:
            ret.append(each)
    return ret


def is_valid_transition(transition_graph, _from, _to):
    """
    Given a transition graph, from and to transitions check whether the
    proposed transition to is valid

    :param transition_graph: dict - Transition graph
    :param _from: string - transtition from
    :param _to: string - transition to
    :return boolean:
    """

    not_in_keys = _to not in expand_list(transition_graph.keys())
    not_in_values = _to not in expand_list(transition_graph.values())
    if not_in_keys and not_in_values:
        raise ValidationError({str(_to): "Target workflow state non existent"})

    if _from not in transition_graph:
        return False

    candidate_destinations = transition_graph[_from]

    return _to in candidate_destinations


def can_skip_transition(skippable_transitions, _from, _to):
    """
    Given a list of transitions, from and to transitions check whether a skip
    is allowed from the 'from' transition to the 'to' transition.

    :param skippable_transitions: list - list of valid transitions
    :param _from: string - transtition from
    :param _to: string - transition to
    :return boolean:
    """
    if _from in skippable_transitions and _to in skippable_transitions and _from == _to:
        return True


def future_states(transition_graph, start_state):
    """
    Computes a list of possible transitions from a certain state.

    :param transition_graph: a dict graph with valid transitions.
    :param start_state: the state to start determining the future
        states from
    """
    possible = []
    graph = copy.deepcopy(transition_graph)
    try:
        to_look_at = graph[start_state][:]
    except KeyError:
        to_look_at = []

    while to_look_at:
        for state in to_look_at:
            to_look_at.remove(state)
            if state not in possible:
                possible.append(state)
                to_look_at.extend(graph.get(state, []))

    return possible
