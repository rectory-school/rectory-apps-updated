# Generated by Django 3.2.16 on 2023-03-04 22:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("evaluations", "0012_tag_created_at"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tagcategory",
            name="admin_filter_display_values",
        ),
    ]
