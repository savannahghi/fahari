# Generated by Django 3.2.7 on 2021-09-21 11:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ops', '0035_weeklyprogramupdatecomment_date_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weeklyprogramupdatecomment',
            name='weekly_update',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ops.weeklyprogramupdate'),
        ),
    ]
