# Generated by Django 3.2.16 on 2023-01-23 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("evaluations", "0004_alter_tag_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="tagcategory",
            name="admin_filter_breakout_values",
            field=models.BooleanField(
                default=False,
                help_text="If the individual values for this tag category should be broken out on the admin filter",
            ),
        ),
        migrations.AddField(
            model_name="tagcategory",
            name="admin_filter_display_values",
            field=models.BooleanField(
                default=False,
                help_text="If the individual values for this tag category should be listed on the admin filter",
            ),
        ),
    ]
