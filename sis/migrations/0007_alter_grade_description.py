# Generated by Django 3.2.7 on 2021-09-06 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sis', '0006_auto_20210906_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grade',
            name='description',
            field=models.CharField(blank=True, max_length=63),
        ),
    ]