from typing import Set
from django.http.request import HttpRequest

import humanize

from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext as _

from solo.admin import SingletonModelAdmin


from . import models


@admin.register(models.SyncConfig)
class SyncConfigAdmin(SingletonModelAdmin):
    fields = [
        "sync_enabled",
        "sync_asap",
        "teacher_group",
        "last_sync_attempt",
        "get_sync_delay",
    ]
    readonly_fields = ["last_sync_attempt", "get_sync_delay"]

    @admin.display(description="Time until next sync")
    def get_sync_delay(self, obj: models.SyncConfig):
        if obj.ready_for_sync:
            return _("ASAP")

        return humanize.naturaldelta(obj.next_sync - timezone.now())


class NoAdd(admin.ModelAdmin):
    """Block addition"""

    def has_add_permission(self, request):
        return False


class NoDelete(admin.ModelAdmin):
    """Block deletion"""

    def has_delete_permission(self, request, obj=None):
        return False


class NoChange(admin.ModelAdmin):
    """Block changes"""

    def has_change_permission(self, request, obj=None):
        return False


class ChangeOnly(NoAdd, NoDelete):
    """Change only permissions"""

    editable_fields: Set[str] = set()

    def get_fields(self, request, obj=None):
        if self.fields:
            return self.fields

        return [f.attname for f in obj._meta.fields if not f.auto_created]

    def get_readonly_fields(self, request, obj):
        fields = set(self.get_fields(request, obj))
        return list(fields - self.editable_fields)


class ReadOnly(NoAdd, NoDelete, NoChange):
    """Read only permissions"""


@admin.register(models.School)
class SchoolAdmin(ReadOnly):
    """Read-only school admin"""

    list_filter = ["active"]
    search_fields = ["name"]
    list_display = ["name", "sis_id", "active"]


class HonorificIsBlankFilter(admin.SimpleListFilter):
    title = "honorific"
    parameter_name = "honorific_status"

    def lookups(self, request, model_admin):
        return (
            ("exists", _("Has honorific")),
            ("empty", _("Lacks honorific")),
        )

    def queryset(self, request, queryset):
        if self.value() == "exists":
            return queryset.exclude(honorific="")

        if self.value() == "empty":
            return queryset.filter(honorific="")

        return queryset


@admin.register(models.Teacher)
class TeacherAdmin(ChangeOnly):
    editable_fields = {"honorific", "formal_name_override"}
    search_fields = ["given_name", "family_name", "email"]
    list_display = [
        "__str__",
        "given_name",
        "family_name",
        "honorific",
        "email",
        "active",
    ]
    list_filter = ["active", "schools", HonorificIsBlankFilter]


@admin.register(models.Student)
class StudentAdmin(ChangeOnly, admin.ModelAdmin):
    """Student admin"""

    editable_fields = {"nickname"}
    search_fields = ["given_name", "family_name", "email"]
    list_display = ["__str__", "given_name", "family_name", "email", "active"]
    list_filter = ["active", "schools"]


@admin.register(models.Course)
class CourseAdmin(ReadOnly, admin.ModelAdmin):
    search_fields = ["title"]


@admin.register(models.Class)
class ClassAdmin(ReadOnly, admin.ModelAdmin):
    search_fields = ["title", "course"]
    list_filter = ["course"]


@admin.register(models.TeacherEnrollment)
class TeacherEnrollmentAdmin(ReadOnly, admin.ModelAdmin):
    search_fields = [
        "teacher__given_name",
        "teacher__family_name",
        "section__course__title",
    ]
    list_filter = ["section__course"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("teacher", "section", "section__course")
        )


@admin.register(models.StudentEnrollment)
class StudentEnrollmentAdmin(ReadOnly, admin.ModelAdmin):
    search_fields = [
        "student__given_name",
        "student__family_name",
        "section__course__title",
    ]
    list_filter = ["section__course"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("student", "section", "section__course")
        )


@admin.register(models.AdvisoryCourse)
class AdvisoryClassAdmin(admin.ModelAdmin):
    """Advisory class admin"""

    autocomplete_fields = ["course"]
    list_display = ["__str__", "course_active"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("course")

    def has_change_permission(  # type: ignore
        self,
        request: HttpRequest,
        obj: models.AdvisoryCourse | None = None,
    ) -> bool:
        if obj and not obj.course.active:
            return False

        return super().has_change_permission(request, obj)

    @admin.decorators.display(description="Course active", boolean=True)
    def course_active(self, obj: models.AdvisoryCourse) -> bool:
        return obj.course.active


@admin.register(models.AdvisorySchool)
class AdvisorySchoolAdmin(admin.ModelAdmin):
    """Advisory school admin"""

    autocomplete_fields = ["school"]
    list_display = ["__str__", "school_active"]

    def has_change_permission(  # type: ignore
        self,
        request: HttpRequest,
        obj: models.AdvisorySchool | None = None,
    ) -> bool:
        if obj and not obj.school.active:
            return False

        return super().has_change_permission(request, obj)

    @admin.decorators.display(description="School active", boolean=True)
    def school_active(self, obj: models.AdvisorySchool) -> bool:
        return obj.school.active
