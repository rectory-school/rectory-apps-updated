from typing import Iterable, List, Optional
from django.db import models
from django.db.models import QuerySet


class Student(models.Model):
    """Basic student model"""

    student_id = models.CharField(
        max_length=256, unique=True, help_text="The SIS Student ID"
    )
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    preferred_first_name = models.CharField(max_length=256, blank=True)
    email = models.EmailField(unique=True)

    @property
    def name(self) -> Optional[str]:
        if self.preferred_first_name and self.last_name:
            return f"{self.preferred_first_name} {self.last_name}"

        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.name}: {self.student_id}"


class Teacher(models.Model):
    """Basic teacher model"""

    teacher_id = models.CharField(max_length=256, unique=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    honorific = models.CharField(max_length=256, blank=True)
    email = models.EmailField(unique=True)

    @property
    def formal_name(self) -> Optional[str]:
        if self.honorific and self.last_name:
            return f"{self.honorific} {self.last_name}"

        return f"{self.last_name}, {self.first_name}"

    @property
    def informal_name(self) -> Optional[str]:
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.name}: {self.teacher_id}"
