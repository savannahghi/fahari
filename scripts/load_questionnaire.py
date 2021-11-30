#!/usr/bin/env python
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Literal, Sequence, TypedDict

import django
from django.db import transaction

# =============================================================================
# CONSTANTS
# =============================================================================

ANSWER_TYPES = Literal[
    "dependent",
    "fraction",
    "int",
    "none",
    "real",
    "select_one",
    "select_multiple",
    "text_answer",
    "yes_no",
]

PRECEDENCE_DISPLAY_TYPES = Literal["bullet", "numbered_td", "lower_case_letters_tcb"]


class QuestionData(TypedDict):
    """The structure of a question dictionary."""

    answer_type: ANSWER_TYPES
    children: Sequence["QuestionData"]  # type: ignore
    metadata: Dict[str, Any]
    precedence: int
    precedence_display_type: PRECEDENCE_DISPLAY_TYPES
    query: str
    question_code: str


class QuestionGroupData(TypedDict):
    """The structure of a question group dictionary."""

    children: Sequence["QuestionGroupData"]  # type: ignore
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
    org,  # "fahari.common.models.Organisation"
    question_data: QuestionData,
    question_group,  # "fahari.sims.models.QuestionGroup"
    parent=None,
):
    from fahari.sims.models import Question

    try:
        question = Question.objects.create(
            **{
                "answer_type": question_data["answer_type"],
                "metadata": question_data["metadata"],
                "organisation": org,
                "parent": parent,
                "precedence": question_data["precedence"],
                "precedence_display_type": question_data.get("precedence_display_type"),
                "query": question_data["query"],
                "question_code": question_data["question_code"],
                "question_group": question_group,
            }
        )
    except Exception as e:
        print("Error saving question %s." % question_data["query"])
        raise e

    if len(question_data["children"]) > 0:
        for _question_data in question_data["children"]:
            _load_question(org, _question_data, question_group, question)


def _load_question_group(
    org,  # "fahari.common.models.Organisation"
    question_group_data: QuestionGroupData,
    questionnaire,  # "fahari.sims.models.Questionnaire"
    parent=None,
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
            _load_question_group(org, _question_group_data, questionnaire, question_group)

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
            _load_question_group(org, question_group_data, questionnaire)
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
