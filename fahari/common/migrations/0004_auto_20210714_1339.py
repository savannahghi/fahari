# Generated by Django 3.1.12 on 2021-07-14 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0003_auto_20210714_1232"),
    ]

    operations = [
        migrations.AlterField(
            model_name="organisation",
            name="created_by",
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="organisation",
            name="updated_by",
            field=models.UUIDField(blank=True, null=True),
        ),
    ]