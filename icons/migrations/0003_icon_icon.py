# Generated by Django 3.2.5 on 2021-07-20 21:49

from django.db import migrations
import icons.models
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('icons', '0002_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='icon',
            name='icon',
            field=sorl.thumbnail.fields.ImageField(default=None, upload_to=icons.models.uuid_upload),
            preserve_default=False,
        ),
    ]
