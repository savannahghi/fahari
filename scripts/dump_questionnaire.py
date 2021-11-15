#!/usr/bin/env python
import json
import os
import sys
from pathlib import Path

import django


def get_organisation():
    from fahari.common.models import Organisation

    return Organisation.objects.get(code=1)


def load_questionnaire(source_path):
    from fahari.sims.models import Question, QuestionGroup, Questionnaire

    org = get_organisation()
    file = open(source_path)
    data = json.load(file)

    questionnaire = Questionnaire.objects.create(
        **{"organisation": org, "name": "SERVICE DELIVERY", "questionnaire_type": "mentorship"}
    )

    try:
        for question_group in data["question_groups"]:
            question_grp = QuestionGroup.objects.create(
                **{
                    "organisation": org,
                    "title": question_group["title"],
                    "questionnaire": questionnaire,
                    "precedence": question_group["precedence"],
                    "precedence_display_type": question_group["precedence_display_type"],
                }
            )
            if question_group["has_children"] is True:
                for question_g in question_group["child_groups"]:
                    question_grp_2 = QuestionGroup.objects.create(
                        **{
                            "organisation": org,
                            "title": question_g["title"],
                            "parent": question_grp,
                            "precedence": question_g["precedence"],
                            "precedence_display_type": question_g["precedence_display_type"],
                        }
                    )
                    if question_g["has_children"] is False:
                        for question in question_g["questions"]:
                            Question.objects.create(
                                **{
                                    "organisation": org,
                                    "query": question["query"],
                                    "answer_type": question["answer_type"],
                                    "question_group": question_grp_2,
                                    "precedence": question["precedence"],
                                }
                            )
                            if question["has_child_question"] is True:
                                for q in question["children"]:
                                    Question.objects.create(
                                        **{
                                            "organisation": org,
                                            "query": q["query"],
                                            "answer_type": q["answer_type"],
                                            "precedence": q["precedence"],
                                        }
                                    )
                            else:
                                Question.objects.create(
                                    **{
                                        "organisation": org,
                                        "query": question["query"],
                                        "answer_type": question["answer_type"],
                                        "precedence": question["precedence"],
                                    }
                                )
                    else:
                        for question_group in question_g["child_groups"]:
                            if question_group["has_children"] is True:
                                for question_gr in question_group["child_groups"]:
                                    question_grp_2 = QuestionGroup.objects.create(
                                        **{
                                            "organisation": org,
                                            "title": question_gr["title"],
                                            "parent": question_grp,
                                            "precedence": question_gr["precedence"],
                                            "precedence_display_type": question_gr[
                                                "precedence_display_type"
                                            ],
                                        }
                                    )
                                    if question_gr["has_children"] is False:
                                        for question in question_gr["questions"]:
                                            Question.objects.create(
                                                **{
                                                    "organisation": org,
                                                    "query": question["query"],
                                                    "answer_type": question["answer_type"],
                                                    "question_group": question_grp_2,
                                                    "precedence": question["precedence"],
                                                }
                                            )
                                            if question["has_child_question"] is True:
                                                for q in question["children"]:
                                                    Question.objects.create(
                                                        **{
                                                            "organisation": org,
                                                            "query": q["query"],
                                                            "answer_type": q["answer_type"],
                                                            "precedence": q["precedence"],
                                                        }
                                                    )
                                            else:
                                                Question.objects.create(
                                                    **{
                                                        "organisation": org,
                                                        "query": question["query"],
                                                        "answer_type": question["answer_type"],
                                                        "precedence": question["precedence"],
                                                    }
                                                )
                            else:
                                for question in question_group["questions"]:
                                    Question.objects.create(
                                        **{
                                            "organisation": org,
                                            "query": question["query"],
                                            "answer_type": question["answer_type"],
                                            "question_group": question_grp_2,
                                            "precedence": question["precedence"],
                                        }
                                    )
                                if question["has_child_question"] is True:
                                    for q in question["children"]:
                                        Question.objects.create(
                                            **{
                                                "organisation": org,
                                                "query": q["query"],
                                                "answer_type": q["answer_type"],
                                                "precedence": q["precedence"],
                                            }
                                        )
                                else:
                                    Question.objects.create(
                                        **{
                                            "organisation": org,
                                            "query": question["query"],
                                            "answer_type": question["answer_type"],
                                            "precedence": question["precedence"],
                                        }
                                    )
            else:
                for question in question_group["questions"]:
                    Question.objects.create(
                        **{
                            "organisation": org,
                            "query": question["query"],
                            "answer_type": question["answer_type"],
                            "question_group": question_grp,
                            "precedence": question["precedence"],
                        }
                    )
                    if question["has_child_question"] is True:
                        for q in question["children"]:
                            Question.objects.create(
                                **{
                                    "organisation": org,
                                    "query": q["query"],
                                    "answer_type": q["answer_type"],
                                    "precedence": q["precedence"],
                                }
                            )
                    else:
                        Question.objects.create(
                            **{
                                "organisation": org,
                                "query": question["query"],
                                "answer_type": question["answer_type"],
                                "precedence": question["precedence"],
                            }
                        )
    except Exception as e:
        raise e


if __name__ == "__main__":
    base_path = Path(__file__).parent.parent.resolve()
    sys.path.append(str(base_path))
    sys.path.append(str(base_path / "fahari"))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
    django.setup()

    data_dir = os.path.join(base_path, "data")
    source_path = os.path.join(data_dir, "service_delivery_questionnaire.json")
    load_questionnaire(source_path)
