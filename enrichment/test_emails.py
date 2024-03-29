"""Tests for the email system"""

from datetime import date, time, datetime, timedelta
from typing import Sequence
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest

from django.conf import settings

import blackbaud.models

from enrichment.emails import (
    get_outgoing_messages,
    unassigned_advisor,
    OutgoingEmail,
    AddressPair,
    comma_format_list,
    deduplicate_address_pairs,
)

from enrichment.models import (
    EmailConfig,
    RelatedAddress,
    Option,
    Slot,
    EMAIL_REPORT_CHOICES,
)

COMMA_LIST_EXPECTATIONS = (
    ((1,), "1"),
    ((1, 2), "1 and 2"),
    ((1, 2, 3), "1, 2, and 3"),
)

DEDUPLICATED_PAIR_EXPECTATIONS = (
    (
        [
            AddressPair("Adam", "adam@example.org"),
            AddressPair("Adam 2", "adam@example.org"),
            AddressPair("Adam 3", "ADAM@example.org"),
        ],
        {
            "adam@example.org",
        },
    ),
    (
        [
            AddressPair("Adam", "adam@example.org"),
            AddressPair("Adam 2", "adam2@example.org"),
            AddressPair("Adam 3", "adam@example.org"),
        ],
        {"adam@example.org", "adam2@example.org"},
    ),
)


@pytest.mark.django_db
@pytest.mark.parametrize("report_name", (choice[0] for choice in EMAIL_REPORT_CHOICES))
def test_generate_email_html(report_name: str):
    middle_school = blackbaud.models.School(
        sis_id=uuid4().hex,
        active=True,
        name="Middle School",
    )
    middle_school.save()

    course = blackbaud.models.Course(
        sis_id=uuid4().hex,
        active=True,
        title="Advisory",
    )
    course.save()

    student = blackbaud.models.Student(
        sis_id=uuid4().hex,
        active=True,
        given_name="Jimmy",
        family_name="Neutron",
        email="example@example.org",
    )
    student.save()
    student.schools.add(middle_school)

    teacher = blackbaud.models.Teacher(
        sis_id=uuid4().hex,
        active=True,
        given_name="Adam",
        family_name="Peacock",
        email="example@example.org",
    )
    teacher.save()

    section = blackbaud.models.Class(
        sis_id=uuid4().hex,
        active=True,
        title="Peacock advising",
        course=course,
        school=middle_school,
    )
    section.save()

    blackbaud.models.TeacherEnrollment.objects.create(
        sis_id=uuid4().hex,
        active=True,
        section=section,
        teacher=teacher,
        school=middle_school,
        begin_date=date.today() - timedelta(days=30),
        end_date=date.today() + timedelta(days=30),
    )

    blackbaud.models.StudentEnrollment.objects.create(
        sis_id=uuid4().hex,
        active=True,
        section=section,
        student=student,
        school=middle_school,
        begin_date=date.today() - timedelta(days=30),
        end_date=date.today() + timedelta(days=30),
    )

    blackbaud.models.AdvisoryCourse.objects.create(course=course)
    blackbaud.models.AdvisorySchool.objects.create(school=middle_school)

    slot = Slot()
    slot.date = date(2022, 10, 11)  # Tuesday
    slot.editable_until = datetime(
        slot.date.year,
        slot.date.month,
        slot.date.day,
        12,
        0,
        0,
        0,
        ZoneInfo("America/New_York"),
    )
    slot.save()

    option = Option()
    option.start_date = date.today() - timedelta(days=7)
    option.end_date = option.start_date + timedelta(days=365)

    option.teacher = teacher
    option.save()

    cfg = EmailConfig()
    cfg.report = report_name
    cfg.start = 0
    cfg.end = 0
    cfg.time = time(11, 0, 0)
    cfg.monday = True
    cfg.tuesday = True
    cfg.wednesday = True
    cfg.thursday = True
    cfg.friday = True
    cfg.saturday = True
    cfg.sunday = True

    cfg.from_name = "Rectory Enrichment System"
    cfg.from_address = "server@apps.rectoryschool.org"

    cfg.save()

    msgs = get_outgoing_messages(cfg, slot.date)

    for msg in msgs:
        assert msg.message_html


@pytest.mark.django_db
@pytest.mark.parametrize("report_name", (choice[0] for choice in EMAIL_REPORT_CHOICES))
def test_generate_email_text(report_name: str):
    middle_school = blackbaud.models.School(
        sis_id=uuid4().hex,
        active=True,
        name="Middle School",
    )
    middle_school.save()

    course = blackbaud.models.Course(
        sis_id=uuid4().hex,
        active=True,
        title="Advisory",
    )
    course.save()

    student = blackbaud.models.Student(
        sis_id=uuid4().hex,
        active=True,
        given_name="Jimmy",
        family_name="Neutron",
        email="example@example.org",
    )
    student.save()
    student.schools.add(middle_school)

    teacher = blackbaud.models.Teacher(
        sis_id=uuid4().hex,
        active=True,
        given_name="Adam",
        family_name="Peacock",
        email="example@example.org",
    )
    teacher.save()

    section = blackbaud.models.Class(
        sis_id=uuid4().hex,
        active=True,
        title="Peacock advising",
        course=course,
        school=middle_school,
    )
    section.save()

    blackbaud.models.TeacherEnrollment.objects.create(
        sis_id=uuid4().hex,
        active=True,
        section=section,
        teacher=teacher,
        school=middle_school,
        begin_date=date.today() - timedelta(days=30),
        end_date=date.today() + timedelta(days=30),
    )

    blackbaud.models.StudentEnrollment.objects.create(
        sis_id=uuid4().hex,
        active=True,
        section=section,
        student=student,
        school=middle_school,
        begin_date=date.today() - timedelta(days=30),
        end_date=date.today() + timedelta(days=30),
    )

    blackbaud.models.AdvisoryCourse.objects.create(course=course)
    blackbaud.models.AdvisorySchool.objects.create(school=middle_school)

    slot = Slot()
    slot.date = date(2022, 10, 11)  # Tuesday
    slot.editable_until = datetime(
        slot.date.year,
        slot.date.month,
        slot.date.day,
        12,
        0,
        0,
        0,
        ZoneInfo("America/New_York"),
    )
    slot.save()

    option = Option()
    option.start_date = date.today() - timedelta(days=7)
    option.end_date = option.start_date + timedelta(days=365)

    option.teacher = teacher
    option.save()

    cfg = EmailConfig()
    cfg.report = report_name
    cfg.start = 0
    cfg.end = 0
    cfg.time = time(11, 0, 0)
    cfg.monday = True
    cfg.tuesday = True
    cfg.wednesday = True
    cfg.thursday = True
    cfg.friday = True
    cfg.saturday = True
    cfg.sunday = True

    cfg.from_name = "Rectory Enrichment System"
    cfg.from_address = "server@apps.rectoryschool.org"

    cfg.save()

    msgs = get_outgoing_messages(cfg, slot.date)

    for msg in msgs:
        assert msg.message_text


@pytest.mark.django_db
def test_advisor_unassigned():
    """A test for a single advisor with a single unassigned student"""

    teacher, student, slot = _basic_setup()

    cfg = EmailConfig()
    cfg.report = "unassigned_advisor"
    cfg.start = 0
    cfg.end = 6
    cfg.time = time(11, 0, 0)
    cfg.monday = True
    cfg.tuesday = True
    cfg.wednesday = True
    cfg.thursday = True
    cfg.friday = True
    cfg.saturday = True
    cfg.sunday = True
    cfg.from_name = "Rectory Enrichment System"
    cfg.from_address = "server@apps.rectoryschool.org"

    cfg.save()

    RelatedAddress.objects.create(
        name="Lisa",
        address="admin-user@rectoryschool.org",
        field="reply-to",
        message=cfg,
    )

    msgs = list(unassigned_advisor(cfg, {slot}))
    assert len(msgs) == 1

    actual = msgs.pop()

    expected = OutgoingEmail(
        cfg=cfg,
        template_name="unassigned_advisor",
        context={
            "advisor": teacher,
            "count": 1,
            "slots": [(slot, [student])],
            "base_url": settings.EMAIL_BASE_URL,
            "deadline": slot.editable_until - timedelta(hours=1),
        },
        subject="You have unassigned advisees",
        to_addresses={AddressPair("Adam Peacock", "example@example.org")},
        cc_addresses=set(),
        bcc_addresses=set(),
        reply_to_addresses=set(),
    )

    assert actual.context == expected.context

    assert actual == expected

    assert actual.message_html is not None
    assert actual.message_text is not None


def _basic_setup():
    middle_school = blackbaud.models.School(
        sis_id=uuid4().hex,
        active=True,
        name="Middle School",
    )
    middle_school.save()

    course = blackbaud.models.Course(
        sis_id=uuid4().hex,
        active=True,
        title="Advisory",
    )
    course.save()

    student = blackbaud.models.Student(
        sis_id=uuid4().hex,
        active=True,
        given_name="Jimmy",
        family_name="Neutron",
        email="example@example.org",
    )
    student.save()
    student.schools.add(middle_school)

    teacher = blackbaud.models.Teacher(
        sis_id=uuid4().hex,
        active=True,
        given_name="Adam",
        family_name="Peacock",
        email="example@example.org",
    )
    teacher.save()

    section = blackbaud.models.Class(
        sis_id=uuid4().hex,
        active=True,
        title="Peacock advising",
        course=course,
        school=middle_school,
    )
    section.save()

    blackbaud.models.TeacherEnrollment.objects.create(
        sis_id=uuid4().hex,
        active=True,
        section=section,
        teacher=teacher,
        school=middle_school,
        begin_date=date.today() - timedelta(days=30),
        end_date=date.today() + timedelta(days=30),
    )

    blackbaud.models.StudentEnrollment.objects.create(
        sis_id=uuid4().hex,
        active=True,
        section=section,
        student=student,
        school=middle_school,
        begin_date=date.today() - timedelta(days=30),
        end_date=date.today() + timedelta(days=30),
    )

    blackbaud.models.AdvisoryCourse.objects.create(course=course)
    blackbaud.models.AdvisorySchool.objects.create(school=middle_school)

    slot = Slot()
    slot.date = date(2022, 10, 11)  # Tuesday
    slot.editable_until = datetime(
        slot.date.year,
        slot.date.month,
        slot.date.day,
        12,
        0,
        0,
        0,
        ZoneInfo("America/New_York"),
    )
    slot.save()

    option = Option()
    option.start_date = date.today() - timedelta(days=7)
    option.end_date = option.start_date + timedelta(days=365)

    option.teacher = teacher
    option.save()

    return teacher, student, slot


@pytest.mark.parametrize(("input", "expected"), COMMA_LIST_EXPECTATIONS)
def test_comma_list(input: Sequence[int], expected: str):
    str_inputs = [str(val) for val in input]
    actual = comma_format_list(str_inputs)
    assert actual == expected


@pytest.mark.parametrize(("input", "expected"), DEDUPLICATED_PAIR_EXPECTATIONS)
def test_deduplicated_addresses(input: list[AddressPair], expected: set[str]):
    actual = deduplicate_address_pairs(input)
    assert len(actual) == len(expected)
