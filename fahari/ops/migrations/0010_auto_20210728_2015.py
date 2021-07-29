# Generated by Django 3.2.5 on 2021-07-28 17:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0017_auto_20210727_1306'),
        ('ops', '0009_alter_sitementorship_duration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyupdate',
            name='came_early',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailyupdate',
            name='clients_booked',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailyupdate',
            name='date',
            field=models.DateField(default=datetime.datetime.today),
        ),
        migrations.AlterField(
            model_name='dailyupdate',
            name='ipt_new_adults',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailyupdate',
            name='ipt_new_paeds',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailyupdate',
            name='kept_appointment',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailyupdate',
            name='missed_appointment',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailyupdate',
            name='new_ft',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailyupdate',
            name='total',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailyupdate',
            name='unscheduled',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterUniqueTogether(
            name='dailyupdate',
            unique_together={('facility', 'date')},
        ),
    ]