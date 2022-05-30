from django.contrib import admin
from django.http import HttpRequest
from pyparsing import Optional
from . import models


class StudentEmailInline(admin.TabularInline):
    model = models.StudentEmail


@admin.register(models.Student)
class StudentAdmin(admin.ModelAdmin):
    """Student admin"""

    fields = ["first_name", "preferred_first_name", "last_name", "email"]
    readonly_fields = ["first_name", "preferred_first_name", "last_name", "email"]
    search_fields = [
        "first_name",
        "last_name",
        "preferred_first_name",
        "email__email",
        "teacher_id",
    ]


class TeacherEmailInline(admin.TabularInline):
    model = models.TeacherEmail


@admin.register(models.Teacher)
class TeacherAdmin(admin.ModelAdmin):
    """Teacher admin"""

    fields = ["honorific", "first_name", "last_name", "email"]
    readonly_fields = ["honorific", "first_name", "last_name", "email"]
    search_fields = [
        "honorific",
        "first_name",
        "last_name",
        "email__email",
        "teacher_id",
    ]

    def has_add_permission(self, request) -> bool:
        del request
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        del request
        del obj

        return False
