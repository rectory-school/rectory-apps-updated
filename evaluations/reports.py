"""Report generator for evaluations"""

from collections.abc import Iterable, Sequence

import io

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    KeepTogether,
    Flowable,
)
from reportlab.lib.styles import ParagraphStyle

from . import models

title_style = ParagraphStyle(name="title")
tag_style = ParagraphStyle(name="tag")
question_style = ParagraphStyle(name="multiple-choice-question")
freeform_question_style = ParagraphStyle(name="freeform-question")
freeform_answer_style = ParagraphStyle(name="freeform-answer")

Answer = models.EvaluationMultipleChoiceAnswer | models.EvaluationFreeformAnswer


class NestedReportGenerator:
    def __init__(
        self,
        question_set: models.QuestionSet,
        categorizers: Iterable[models.TagCategory],
    ):
        self.question_set = question_set
        self.categorizers = categorizers


def generate_report(
    out: io.BytesIO,
    question_set: models.QuestionSet,
    tags: Sequence[models.Tag],
    multiple_choice_answers: Sequence[models.EvaluationMultipleChoiceAnswer],
    freeform_answers: Sequence[models.EvaluationFreeformAnswer],
):
    """Generate a single PDF report from a single set of answers"""

    tag_set = set(tags)

    story = []
    for tag in tags:
        tag_title = f"{tag.category.name}: {tag.value}"
        story.append(Paragraph(tag_title))

    multiple_choice_questions: Sequence[
        models.MultipleChoiceQuestion
    ] = question_set.multiple_choice_questions.all()  # type: ignore

    for q_mc in multiple_choice_questions:
        story.extend(_mc_answer_flowables(tag_set, q_mc, multiple_choice_answers))

    freeform_questions: Sequence[
        models.FreeformQuestion
    ] = question_set.freeform_questions.all()  # type: ignore

    for q_ff in freeform_questions:
        story.extend(_freeform_answer_flowables(tag_set, q_ff, freeform_answers))

    doc = SimpleDocTemplate(out)
    doc.build(story)


def _mc_answers_for_question_aggregate(
    available_answers: Sequence[models.MultipleChoiceAnswer],
    tags: set[models.Tag],
    evaluation_answers: Sequence[models.EvaluationMultipleChoiceAnswer],
) -> dict[models.MultipleChoiceAnswer, int]:
    """Get the aggregated selected answers for a given question"""

    out = {answer: 0 for answer in available_answers}

    for answer in evaluation_answers:
        if _evaluation_is_relevant(tags, answer.evaluation):
            out[answer.answer] += 1

    return out


def _evaluation_is_relevant(
    required_tags: set[models.Tag],
    evaluation: models.Evaluation,
) -> bool:
    evaluation_tags: set[models.Tag] = set(evaluation.tags.all())

    # Example:
    #  Required tags: Adam, Python 101
    #  Evaluation tags: Adam, Python 101, Fall 2023 - should be included
    # The evaluation tags have to be a superset of the required tags
    # If the required tags were Adam, Python 201, then it wouldn't be a superset
    # of the required tags.

    return evaluation_tags.issuperset(required_tags)


def _mc_answer_flowables(
    tags: set[models.Tag],
    question: models.MultipleChoiceQuestion,
    evaluation_answers: Sequence[models.EvaluationMultipleChoiceAnswer],
) -> list[Flowable]:
    """Get the flowable(s) for a given question"""

    available_answers: Sequence[
        models.MultipleChoiceAnswer
    ] = question.answers.all()  # type: ignore

    count_aggregate = _mc_answers_for_question_aggregate(
        available_answers, tags, evaluation_answers
    )

    counts = sorted(count_aggregate.items(), key=lambda item: item[0].position)

    answer_table_row = [
        Paragraph(f"{answer.answer}: {count}") for answer, count in counts
    ]

    together = KeepTogether(
        [
            Paragraph(question.question, question_style),
            Table(data=[answer_table_row]),
        ]
    )

    return [together]


def _freeform_answer_flowables(
    tags: set[models.Tag],
    question: models.FreeformQuestion,
    answers: Sequence[models.EvaluationFreeformAnswer],
) -> list[Flowable]:
    """Get the flowable(s) for a given set of freeform choice answers"""

    question_answers = [
        obj
        for obj in answers
        if obj.question == question and _evaluation_is_relevant(tags, obj.evaluation)
    ]

    together: list[Flowable] = [Paragraph(question.question, freeform_question_style)]

    for answer in question_answers:
        together.append(Paragraph(answer.answer, freeform_answer_style))

    # We want to keep all the answers on one page with the question,
    # so we use a KeepTogether here
    return [KeepTogether(together)]
