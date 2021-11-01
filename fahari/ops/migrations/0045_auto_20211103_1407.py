# Generated by Django 3.2.7 on 2021-11-03 11:07

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ops', '0044_alter_mentorshipquestionnaire_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='numbering',
            field=models.CharField(default='(i)', max_length=5),
        ),
        migrations.AddField(
            model_name='questiongroup',
            name='numbering',
            field=models.CharField(default='(a)', max_length=5),
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='numbering',
            field=models.CharField(default='A.', max_length=5),
        ),
        migrations.AlterField(
            model_name='mentorshipquestionnaire',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 3, 11, 7, 50, 161515, tzinfo=utc), editable=False),
        ),
    ]
