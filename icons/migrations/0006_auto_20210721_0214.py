# Generated by Django 3.2.5 on 2021-07-21 02:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('icons', '0005_auto_20210721_0206'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PageIconDisplay',
            new_name='PageItem',
        ),
        migrations.AlterUniqueTogether(
            name='pageitem',
            unique_together={('page', 'icon')},
        ),
        migrations.CreateModel(
            name='FolderIcon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveSmallIntegerField(blank=True, default=0, null=True)),
                ('folder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='icons.folder')),
                ('icon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='icons.icon')),
            ],
            options={
                'ordering': ['position'],
                'unique_together': {('folder', 'icon')},
            },
        ),
    ]
