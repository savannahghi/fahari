# Generated by Django 3.2.9 on 2021-11-16 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sims', '0003_alter_questiongroup_questionnaire'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionanswer',
            name='answered_on',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
