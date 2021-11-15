#!/usr/bin/env python
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Sequence, TypedDict

import django
from django.db import transaction

# =============================================================================
# CONSTANTS
# =============================================================================

ANSWER_TYPES = Literal[
    "dependent",
    "fraction",
    "none",
    "numbe",
    "paragraph",
    "radio_option",
    "ratio",
    "select_list",
    "short_answer",
    "true_false",
    "yes_no",
]

PRECEDENCE_DISPLAY_TYPES = Literal["bullet", "numbered_td", "lower_case_letters_tcb"]


class QuestionData(TypedDict):
    """The structure of a question dictionary."""

    answer_type: ANSWER_TYPES
    children: Sequence["QuestionData"]
    metadata: Dict[str, Any]
    precedence: int
    precedence_display_type: PRECEDENCE_DISPLAY_TYPES
    query: str


class QuestionGroupData(TypedDict):
    """The structure of a question group dictionary."""

    children: Sequence["QuestionGroupData"]
    precedence: int
    precedence_display_type: PRECEDENCE_DISPLAY_TYPES
    questions: Sequence[QuestionData]
    title: str


# =============================================================================
# HELPERS
# =============================================================================


def get_organisation():
    from fahari.common.models import Organisation

    return Organisation.objects.get(code=1)


def _load_question(
    org: "fahari.common.models.Organisation",  # noqa
    question_data: QuestionData,
    question_group: Optional["fahari.sims.models.QuestionGroup"] = None,  # noqa
    parent: Optional["fahari.sims.models.Question"] = None,  # noqa
):
    from fahari.sims.models import Question

    question = Question.objects.create(
        **{
            "answer_type": question_data["answer_type"],
            "metadata": question_data["metadata"],
            "organisation": org,
            "parent": parent,
            "precedence": question_data["precedence"],
            "precedence_display_type": question_data["precedence_display_type"],
            "query": question_data["query"],
            "question_group": question_group,
        }
    )
    if len(question_data["children"]) > 0:
        for _question_data in question_data["children"]:
            _load_question(org, _question_data, None, question)


def _load_question_group(
    org: "fahari.common.models.Organisation",  # noqa
    question_group_data: QuestionGroupData,
    questionnaire: Optional["fahari.sims.models.Questionnaire"] = None,  # noqa
    parent: Optional["fahari.sims.models.QuestionGroup"] = None,  # noqa
) -> None:
    from fahari.sims.models import QuestionGroup

    question_group = QuestionGroup.objects.create(
        **{
            "organisation": org,
            "parent": parent,
            "precedence": question_group_data["precedence"],
            "precedence_display_type": question_group_data["precedence_display_type"],
            "questionnaire": questionnaire,
            "title": question_group_data["title"],
        }
    )
    if len(question_group_data["children"]) > 0:
        for _question_group_data in question_group_data["children"]:
            _load_question_group(org, _question_group_data, None, question_group)

    for question_data in question_group_data["questions"]:
        _load_question(org, question_data, question_group)


@transaction.atomic
def load_questionnaire(source_file):
    from fahari.sims.models import Questionnaire

    org = get_organisation()
    data = json.load(open(file=source_file))
    questionnaire = Questionnaire.objects.create(
        **{"name": "Service Delivery", "questionnaire_type": "mentorship", "organisation": org}
    )

    try:
        question_group_data: QuestionGroupData
        for question_group_data in data["question_groups"]:
            _load_question_group(org, question_group_data, questionnaire, None)
    except Exception as e:
        print("Error loading question group: %s" % question_group_data["title"])  # noqa
        raise e


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    base_path = Path(__file__).parent.parent.resolve()
    sys.path.append(str(base_path))
    sys.path.append(str(base_path / "fahari"))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
    django.setup()

    data_dir = os.path.join(base_path, "data")
    source_path = os.path.join(data_dir, "service_delivery_questionnaire.json")
    load_questionnaire(source_path)