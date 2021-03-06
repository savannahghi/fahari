# Generated by Django 3.2.7 on 2021-09-14 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0022_auto_20210914_1403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='system',
            name='pattern',
            field=models.CharField(choices=[('poc', 'Point of Care'), ('rde', 'Retrospective Data Entry'), ('hybrid', 'Hybrid'), ('none', 'None')], default='none', max_length=100),
        ),
        migrations.AlterField(
            model_name='userfacilityallotment',
            name='allotment_type',
            field=models.CharField(choices=[('facility', 'By Facility'), ('region', 'By Region'), ('both', 'By Both Facility and Region')], max_length=100),
        ),
    ]
