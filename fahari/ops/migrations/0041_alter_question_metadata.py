# Generated by Django 3.2.7 on 2021-10-26 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ops', '0040_auto_20211026_1536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='metadata',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]
