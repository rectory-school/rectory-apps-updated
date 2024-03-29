# Generated by Django 3.2.16 on 2022-10-24 16:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("stored_mail", "0005_alter_relatedaddress_unique_together"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExtraHeader",
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
                ("key", models.CharField(max_length=255)),
                ("value", models.CharField(max_length=4096)),
                (
                    "message",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="extra_headers",
                        to="stored_mail.outgoingmessage",
                    ),
                ),
            ],
            options={
                "unique_together": {("message", "key")},
            },
        ),
    ]
