# Generated by Django 3.2.6 on 2021-09-08 10:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ops', '0022_auto_20210907_1119'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commodity',
            name='unit_of_measure',
        ),
        migrations.AddField(
            model_name='commodity',
            name='pack_sizes',
            field=models.ManyToManyField(help_text='Valid pack sizes for this commodity.', to='ops.UoM'),
        ),
        migrations.RemoveField(
            model_name='stockreceiptverification',
            name='unit_of_measure',
        ),
        migrations.AddField(
            model_name='stockreceiptverification',
            name='pack_size',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ops.uom'),
        ),
    ]
