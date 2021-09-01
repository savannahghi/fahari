# Generated by Django 3.2.6 on 2021-09-01 10:31

from django.db import migrations, models
import fahari.common.models


class Migration(migrations.Migration):

    dependencies = [
        ('ops', '0018_facilitysystemticket_resolve_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='weeklyprogramupdate',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=fahari.common.models.get_directory),
        ),
        migrations.AddField(
            model_name='weeklyprogramupdate',
            name='title',
            field=models.CharField(default='-', max_length=255),
        ),
    ]
