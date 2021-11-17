# Generated by Django 3.2.9 on 2021-11-17 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sims', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionanswer',
            name='is_not_applicable',
            field=models.BooleanField(default=False, help_text='Indicates that answer is not applicable for the attached question.'),
        ),
    ]
