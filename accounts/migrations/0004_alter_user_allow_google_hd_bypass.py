# Generated by Django 3.2.13 on 2022-05-29 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_user_allow_google_hd_bypass"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="allow_google_hd_bypass",
            field=models.BooleanField(
                default=False,
                help_text="Allow Google login even if the user isn't in an allowed domain",
                verbose_name="Allow off-workspace Google login",
            ),
        ),
    ]