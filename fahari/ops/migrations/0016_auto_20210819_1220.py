# Generated by Django 3.2.6 on 2021-08-19 09:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ops', '0015_auto_20210819_0900'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='commodity',
            options={'ordering': ('-updated', '-created'), 'verbose_name_plural': 'commodities'},
        ),
        migrations.AddField(
            model_name='commodity',
            name='is_lab_commodity',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='commodity',
            name='is_pharmacy_commodity',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='stockreceiptverification',
            name='delivery_date',
            field=models.DateField(default=datetime.datetime.today),
        ),
    ]
