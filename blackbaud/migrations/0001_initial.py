# Generated by Django 3.2.13 on 2022-09-15 03:18

from django.db import migrations, models
import django.db.models.deletion
from django_safemigrate import Safe


class Migration(migrations.Migration):
    safe = Safe.before_deploy
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Class",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sis_id", models.CharField(max_length=256, unique=True)),
                ("active", models.BooleanField()),
                ("title", models.CharField(max_length=4096)),
            ],
            options={
                "verbose_name_plural": "classes",
                "ordering": ["course__title", "title"],
            },
        ),
        migrations.CreateModel(
            name="Course",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sis_id", models.CharField(max_length=256, unique=True)),
                ("active", models.BooleanField()),
                ("title", models.CharField(max_length=4096)),
            ],
            options={
                "ordering": ["title"],
            },
        ),
        migrations.CreateModel(
            name="School",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sis_id", models.CharField(max_length=256, unique=True)),
                ("active", models.BooleanField()),
                ("name", models.CharField(max_length=4096)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sis_id", models.CharField(max_length=256, unique=True)),
                ("active", models.BooleanField()),
                ("given_name", models.CharField(max_length=256)),
                ("family_name", models.CharField(max_length=256)),
                ("nickname", models.CharField(blank=True, max_length=256)),
                ("email", models.EmailField(max_length=4096)),
                ("grade", models.CharField(max_length=256)),
                ("schools", models.ManyToManyField(to="blackbaud.School")),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="SyncConfig",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("last_sync_attempt", models.DateTimeField(null=True)),
                ("sync_enabled", models.BooleanField(default=True)),
                (
                    "sync_asap",
                    models.BooleanField(default=False, verbose_name="Sync ASAP"),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Teacher",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sis_id", models.CharField(max_length=256, unique=True)),
                ("active", models.BooleanField()),
                ("given_name", models.CharField(max_length=256)),
                ("family_name", models.CharField(max_length=256)),
                ("email", models.EmailField(max_length=4096)),
                ("honorific", models.CharField(blank=True, max_length=8)),
                ("formal_name_override", models.CharField(blank=True, max_length=256)),
                ("schools", models.ManyToManyField(to="blackbaud.School")),
            ],
            options={
                "ordering": ["family_name", "given_name"],
            },
        ),
        migrations.CreateModel(
            name="TeacherEnrollment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sis_id", models.CharField(max_length=256, unique=True)),
                ("active", models.BooleanField()),
                ("begin_date", models.DateField()),
                ("end_date", models.DateField()),
                (
                    "school",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="blackbaud.school",
                    ),
                ),
                (
                    "section",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="blackbaud.class",
                    ),
                ),
                (
                    "teacher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="blackbaud.teacher",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="StudentEnrollment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sis_id", models.CharField(max_length=256, unique=True)),
                ("active", models.BooleanField()),
                ("begin_date", models.DateField()),
                ("end_date", models.DateField()),
                (
                    "school",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="blackbaud.school",
                    ),
                ),
                (
                    "section",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="blackbaud.class",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="blackbaud.student",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="class",
            name="course",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING, to="blackbaud.course"
            ),
        ),
        migrations.AddField(
            model_name="class",
            name="school",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING, to="blackbaud.school"
            ),
        ),
        migrations.AddField(
            model_name="class",
            name="students",
            field=models.ManyToManyField(
                through="blackbaud.StudentEnrollment", to="blackbaud.Student"
            ),
        ),
        migrations.AddField(
            model_name="class",
            name="teachers",
            field=models.ManyToManyField(
                through="blackbaud.TeacherEnrollment", to="blackbaud.Teacher"
            ),
        ),
    ]
