# Generated by Django 3.2.7 on 2021-10-28 11:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ops', '0035_auto_20211028_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booleananswer',
            name='answer_date',
            field=models.DateTimeField(default=datetime.datetime.today),
        ),
        migrations.AlterField(
            model_name='mentorshipquestionnaire',
            name='submit_date',
            field=models.DateTimeField(default=datetime.datetime.today),
        ),
        migrations.AlterField(
            model_name='numberanswer',
            name='answer_date',
            field=models.DateTimeField(default=datetime.datetime.today),
        ),
        migrations.AlterField(
            model_name='paragraphanswer',
            name='answer_date',
            field=models.DateTimeField(default=datetime.datetime.today),
        ),
        migrations.AlterField(
            model_name='questiongroup',
            name='entry_date',
            field=models.DateTimeField(default=datetime.datetime.today),
        ),
        migrations.AlterField(
            model_name='radiooptionanswer',
            name='answer_date',
            field=models.DateTimeField(default=datetime.datetime.today),
        ),
        migrations.AlterField(
            model_name='selectlistanswer',
            name='answer_date',
            field=models.DateTimeField(default=datetime.datetime.today),
        ),
        migrations.AlterField(
            model_name='shortanswer',
            name='answer_date',
            field=models.DateTimeField(default=datetime.datetime.today),
        ),
    ]
