# Generated by Django 3.2.9 on 2022-01-09 13:06

from django.db import migrations, models
import fahari.sims.models


class Migration(migrations.Migration):

    dependencies = [
        ('sims', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='questionanswer',
            managers=[
                ('objects', fahari.sims.models.QuestionAnswerManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='questionnaireresponses',
            managers=[
                ('objects', fahari.sims.models.QuestionnaireResponsesManager()),
            ],
        ),
        migrations.AlterField(
            model_name='question',
            name='answer_type',
            field=models.CharField(choices=[('fraction', 'Fraction'), ('int', 'Whole Number'), ('none', 'Not Applicable'), ('real', 'Real Number'), ('select_one', 'Select One'), ('select_multiple', 'Select Multiple'), ('text', 'Text Answer'), ('yes_no', 'Yes/No')], default='text', help_text='Expected answer type', max_length=15),
        ),
    ]
