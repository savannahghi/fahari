# Generated by Django 3.2.9 on 2021-11-10 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sims', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionanswer',
            name='comments',
            field=models.TextField(blank=True, null=True),
        ),
    ]
