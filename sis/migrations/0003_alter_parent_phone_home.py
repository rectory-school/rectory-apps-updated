# Generated by Django 3.2.7 on 2021-09-07 04:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sis', '0002_auto_20210906_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parent',
            name='phone_home',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
