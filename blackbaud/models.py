from datetime import datetime, timedelta
from django.db import models
from django.utils.translation import gettext as _
from django.utils import timezone
from django.conf import settings

from solo.models import SingletonModel


class SyncConfig(SingletonModel):
    """Sync config for connecting with BlackBaud"""

    last_sync_attempt = models.DateTimeField(null=True)
    sync_enabled = models.BooleanField(default=True)
    sync_asap = models.BooleanField(default=False, verbose_name="Sync ASAP")

    @property
    def next_sync(self) -> datetime:
        if not self.last_sync_attempt or self.sync_asap:
            return timezone.now()

        return self.last_sync_attempt + timedelta(seconds=settings.SIS_SYNC_INTERVAL)

    @property
    def ready_for_sync(self) -> bool:
        return self.next_sync <= timezone.now()

    def __str__(self):
        return _("Blackbaud sync config")


class SISModel(models.Model):
    """Base model for all SIS models"""

    sis_id = models.CharField(max_length=256, unique=True)
    active = models.BooleanField()

    class Meta:
        abstract = True


class School(SISModel):
    name = models.CharField(max_length=4096)

    def __str__(self):
        return self.name


class Teacher(SISModel):
    given_name = models.CharField(max_length=256)
    family_name = models.CharField(max_length=256)
    email = models.EmailField(max_length=4096)
    honorific = models.CharField(max_length=8, blank=True)
    formal_name_override = models.CharField(max_length=256, blank=True)
    schools = models.ManyToManyField(School)

    class Meta:
        ordering = ["family_name", "given_name"]

    @property
    def full_name(self):
        return f"{self.given_name} {self.family_name}"

    @property
    def last_name_first(self):
        return f"{self.family_name}, {self.given_name}"

    @property
    def formal_name(self):
        if self.formal_name_override:
            return self.formal_name_override

        if self.honorific:
            return f"{self.honorific} {self.family_name}"

        return f"M. {self.family_name}"

    def __str__(self):
        return self.full_name


class Student(SISModel):
    given_name = models.CharField(max_length=256)
    family_name = models.CharField(max_length=256)
    nickname = models.CharField(max_length=256, blank=True)

    email = models.EmailField(max_length=4096)
    grade = models.CharField(max_length=256)
    schools = models.ManyToManyField(School)

    @property
    def display_name(self):
        if self.nickname:
            return f"{self.nickname} {self.family_name}"

        return f"{self.given_name} {self.family_name}"

    def __str__(self):
        return self.display_name


class Course(SISModel):
    title = models.CharField(max_length=4096)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Class(SISModel):
    title = models.CharField(max_length=4096)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    school = models.ForeignKey(School, on_delete=models.DO_NOTHING)

    teachers = models.ManyToManyField(Teacher, through="TeacherEnrollment")
    students = models.ManyToManyField(Student, through="StudentEnrollment")

    class Meta:
        verbose_name_plural = "classes"
        ordering = ["course__title", "title"]

    def __str__(self):
        return self.title


class TeacherEnrollment(SISModel):
    section = models.ForeignKey(Class, on_delete=models.DO_NOTHING)
    teacher = models.ForeignKey(Teacher, on_delete=models.DO_NOTHING)
    school = models.ForeignKey(School, on_delete=models.DO_NOTHING)

    begin_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.section}: {self.teacher}"


class StudentEnrollment(SISModel):
    section = models.ForeignKey(Class, on_delete=models.DO_NOTHING)
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    school = models.ForeignKey(School, on_delete=models.DO_NOTHING)

    begin_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.section}: {self.student}"