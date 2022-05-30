from typing import Iterable, List, Optional
from django.db import models
from django.db.models import QuerySet


class StudentManager(models.Manager):
    def get_queryset(self) -> QuerySet["Student"]:
        qs = super().get_queryset()
        qs = qs.select_related("email")
        return qs


class Student(models.Model):
    """Basic student model"""

    student_id = models.CharField(
        max_length=256, unique=True, help_text="The SIS Student ID"
    )
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    preferred_first_name = models.CharField(max_length=256, blank=True)

    objects = StudentManager()

    @property
    def name(self) -> Optional[str]:
        if self.preferred_first_name and self.last_name:
            return f"{self.preferred_first_name} {self.last_name}"

        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"

        return None

    def __str__(self):
        if name := self.name:
            return f"Student {self.student_id} {name}"

        return f"Student {self.student_id}"


class StudentEmail(models.Model):
    """A unique student email, since students might not
    have emails when they are first enrolled"""

    student = models.OneToOneField(
        Student, related_name="email", on_delete=models.CASCADE
    )
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


class Teacher(models.Model):
    """Basic teacher model"""

    teacher_id = models.CharField(max_length=256, unique=True)
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    honorific = models.CharField(max_length=256, blank=True)

    @property
    def formal_name(self) -> Optional[str]:
        if self.honorific and self.last_name:
            return f"{self.honorific} {self.last_name}"

        if self.first_name and self.last_name:
            return f"{self.last_name}, {self.first_name}"

        return None

    @property
    def informal_name(self) -> Optional[str]:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"

        return self.formal_name

    def __str__(self):
        if name := self.informal_name:
            return f"Teacher {self.teacher_id}: {name}"

        return f"Teacher {self.teacher_id}"


class TeacherEmail(models.Model):
    """A unique teacher email, since teachers might not
    have emails when they are first enrolled"""

    teacher = models.OneToOneField(
        Teacher, related_name="email", on_delete=models.CASCADE
    )
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
