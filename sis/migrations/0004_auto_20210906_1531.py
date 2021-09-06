# Generated by Django 3.2.7 on 2021-09-06 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sis', '0003_remove_student_current'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='course_name_short',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='course',
            name='course_name_transcript',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='course',
            name='course_type',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='course',
            name='department',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='course',
            name='division',
            field=models.CharField(blank=True, max_length=2),
        ),
        migrations.AlterField(
            model_name='student',
            name='first_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='student',
            name='last_name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
