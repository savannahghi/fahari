# Generated by Django 3.2.6 on 2021-09-01 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ops', '0020_auto_20210902_0920'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockreceiptverification',
            name='delivery_note_image',
            field=models.ImageField(blank=True, null=True, upload_to='ops/stock_receipts/delivery_notes/', verbose_name='Delivery note photograph'),
        ),
    ]
