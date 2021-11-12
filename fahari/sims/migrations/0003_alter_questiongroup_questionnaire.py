# Generated by Django 3.2.9 on 2021-11-11 15:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sims', '0002_auto_20211111_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questiongroup',
            name='questionnaire',
            field=models.ForeignKey(blank=True, help_text='The questionnaire that a question group belongs to. This should only be provided for question groups that are not sub-questions groups of other question groups.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='question_groups', to='sims.questionnaire'),
        ),
    ]
