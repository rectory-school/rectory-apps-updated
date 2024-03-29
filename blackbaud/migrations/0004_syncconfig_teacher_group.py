# Generated by Django 3.2.16 on 2022-10-25 15:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("blackbaud", "0003_auto_20220917_1205"),
    ]

    operations = [
        migrations.AddField(
            model_name="syncconfig",
            name="teacher_group",
            field=models.ForeignKey(
                blank=True,
                help_text="The group to put all teachers in",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="auth.group",
            ),
        ),
    ]
