# Generated by Django 3.2.9 on 2021-11-29 22:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OutgoingMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_name', models.CharField(max_length=255)),
                ('from_address', models.EmailField(max_length=254)),
                ('subject', models.CharField(blank=True, max_length=4096)),
                ('text', models.TextField(blank=True)),
                ('html', models.TextField(blank=True)),
                ('amp_html', models.TextField(blank=True)),
                ('sent_at', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SendAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('address', models.EmailField(max_length=254)),
                ('field', models.CharField(choices=[('to', 'To'), ('cc', 'Cc'), ('bcc', 'Bcc')], max_length=3)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stored_mail.outgoingmessage')),
            ],
            options={
                'unique_together': {('address', 'message')},
            },
        ),
    ]