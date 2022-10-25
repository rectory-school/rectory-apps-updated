# Generated by Django 3.2.16 on 2022-10-25 16:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("enrichment", "0010_alter_signup_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="signup",
            options={
                "permissions": (
                    (
                        "edit_past_lockout",
                        "Can edit enrichment signups past the lockout time",
                    ),
                    (
                        "set_admin_locked",
                        "Can set/unset admin locked, as well as ignore the flag usage",
                    ),
                    (
                        "use_admin_only_options",
                        "Can assign students to admin only options",
                    ),
                    ("assign_all_advisees", "Can assign any advisees"),
                    ("assign_other_advisees", "Can assign advisees for other advisors"),
                    ("view_reports", "Can view enrichment reports"),
                )
            },
        ),
    ]
