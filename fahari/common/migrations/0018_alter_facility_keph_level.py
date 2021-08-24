# Generated by Django 3.2.6 on 2021-08-24 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0017_auto_20210727_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facility',
            name='keph_level',
            field=models.CharField(blank=True, choices=[('Level 1', 'Level 1'), ('Level 2', 'Level 2'), ('Level 3', 'Level 3'), ('Level 4', 'Level 4'), ('Level 5', 'Level 5'), ('Level 6', 'Level 6')], max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='facility',
            name='owner_type',
            field=models.CharField(blank=True, choices=[('Private Practice', 'Private Practice'), ('Ministry of Health', 'Ministry of Health'), ('Faith Based Organization', 'Faith Based Organization'), ('Non-Governmental Organizations', 'Non-Governmental Organizations')], max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='facility',
            name='constituency',
            field=models.CharField(blank=True, choices=[('Dagoretti North', 'Dagoretti North'),
                                                        ('Dagoretti South', 'Dagoretti South'),
                                                        ('Embakasi Central', 'Embakasi Central'),
                                                        ('Embakasi East', 'Embakasi East'),
                                                        ('Embakasi North', 'Embakasi North'),
                                                        ('Embakasi South', 'Embakasi South'),
                                                        ('Embakasi West', 'Embakasi West'),
                                                        ('Kajiado Central', 'Kajiado Central'),
                                                        ('Kajiado East', 'Kajiado East'),
                                                        ('Kajiado North', 'Kajiado North'),
                                                        ('Kajiado West', 'Kajiado West'), ('Kamukunji', 'Kamukunji'),
                                                        ('Kasarani', 'Kasarani'), ('Kibra', 'Kibra'),
                                                        ('Langata', 'Langata'), ('Magadi', 'Magadi'),
                                                        ('Makadara', 'Makadara'), ('Mathare', 'Mathare'),
                                                        ('Roysambu', 'Roysambu'), ('Ruaraka', 'Ruaraka'),
                                                        ('Starehe', 'Starehe'), ('Westlands', 'Westlands')],
                                   max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='facility',
            name='county',
            field=models.CharField(choices=[('Nairobi', 'Nairobi'), ('Kajiado', 'Kajiado')], max_length=64),
        ),
        migrations.AlterField(
            model_name='facility',
            name='facility_type',
            field=models.CharField(blank=True, choices=[('Basic Health Centre', 'Basic Health Centre'),
                                                        ('Comprehensive Teaching & Tertiary Referral Hospital', 'Comprehensive Teaching & Tertiary Referral Hospital'),
                                                        ('Comprehensive health Centre', 'Comprehensive health Centre'),
                                                        ('Dental Clinic', 'Dental Clinic'),
                                                        ('Dialysis Center', 'Dialysis Center'),
                                                        ('Dispensaries and clinic-out patient only', 'Dispensaries and clinic-out patient only'),
                                                        ('Dispensary', 'Dispensary'),
                                                        ('Farewell Home', 'Farewell Home'),
                                                        ('Health Centre', 'Health Centre'),
                                                        ('Laboratory', 'Laboratory'),
                                                        ('Medical Center', 'Medical Center'),
                                                        ('Medical Clinic', 'Medical Clinic'),
                                                        ('Nursing Homes', 'Nursing Home'),
                                                        ('Nursing and Maternity Home', 'Nursing and Maternity Home'),
                                                        ('Ophthalmology', 'Ophthalmology'), ('Pharmacy', 'Pharmacy'),
                                                        ('Primary care hospitals', 'Primary care hospital'),
                                                        ('Radiology Clinic', 'Radiology Clinic'),
                                                        ('Rehab. Center - Drug and Substance abuse', 'Rehab. Center - Drug and Substance abuse'),
                                                        ('Secondary care hospitals', 'Secondary care hospital'),
                                                        ('Specialized & Tertiary Referral hospitals', 'Specialized & Tertiary Referral hospital'),
                                                        ('VCT', 'VCT')],
                                   max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='facility',
            name='facility_type_category',
            field=models.CharField(blank=True,
                                   choices=[('DISPENSARY', 'Dispensary'), ('HEALTH CENTRE', 'Health Centre'),
                                            ('HOSPITALS', 'Hospital'), ('MEDICAL CENTER', 'Medical Center'),
                                            ('MEDICAL CLINIC', 'Medical Clinic'), ('NURSING HOME', 'Nursing Home'),
                                            ('Primary health  care services', 'Primary Health Care Service'),
                                            ('STAND ALONE', 'Stand Alone')], max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='facility',
            name='sub_county',
            field=models.CharField(blank=True, choices=[('Dagoretti North', 'Dagoretti North'),
                                                        ('Dagoretti South', 'Dagoretti South'),
                                                        ('Embakasi Central', 'Embakasi Central'),
                                                        ('Embakasi East', 'Embakasi East'),
                                                        ('Embakasi North', 'Embakasi North'),
                                                        ('Embakasi South', 'Embakasi South'),
                                                        ('Embakasi West', 'Embakasi West'),
                                                        ('Kajiado Central', 'Kajiado Central'),
                                                        ('Kajiado East', 'Kajiado East'),
                                                        ('Kajiado North', 'Kajiado North'),
                                                        ('Kajiado West', 'Kajiado West'), ('Kamukunji', 'Kamukunji'),
                                                        ('Kasarani', 'Kasarani'), ('Kibra', 'Kibra'),
                                                        ('Langata', 'Langata'), ('Loitokitok', 'Loitokitok'),
                                                        ('Makadara', 'Makadara'), ('Mathare', 'Mathare'),
                                                        ('Roysambu', 'Roysambu'), ('Ruaraka', 'Ruaraka'),
                                                        ('Starehe', 'Starehe'), ('Westlands', 'Westlands')],
                                   max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='facility',
            name='ward',
            field=models.CharField(blank=True, choices=[('Airbase', 'Airbase'), ('Babandogo', 'Babandogo'),
                                                        ('California', 'California'), ('Clay City', 'Clay City'),
                                                        ('Dalalekutuk', 'Dalalekutuk'),
                                                        ('Dandora Area I', 'Dandora Area I'),
                                                        ('Dandora Area II', 'Dandora Area II'),
                                                        ('Dandora Area III', 'Dandora Area III'),
                                                        ('Dandora Area Iv', 'Dandora Area Iv'),
                                                        ('Eastleigh North', 'Eastleigh North'),
                                                        ('Eastleigh South', 'Eastleigh South'),
                                                        ('Embakasi', 'Embakasi'),
                                                        ('Entonet/Lenkism', 'Entonet/Lenkism'),
                                                        ("Ewuaso Oo Nkidong'i", "Ewuaso Oo Nkidong'i"),
                                                        ('Gatini', 'Gatini'), ('Githurai', 'Githurai'),
                                                        ('Harambee', 'Harambee'), ('Hospital', 'Hospital'),
                                                        ('Huruma', 'Huruma'), ('Ildamat', 'Ildamat'),
                                                        ('Iloodokilani', 'Iloodokilani'),
                                                        ('Imara Daima', 'Imara Daima'), ('Imaroro', 'Imaroro'),
                                                        ('Imbrikani/Eselelnkei', 'Imbrikani/Eselelnkei'),
                                                        ('Kabiro', 'Kabiro'), ('Kahawa', 'Kahawa'),
                                                        ('Kahawa West', 'Kahawa West'), ('Kangemi', 'Kangemi'),
                                                        ('Kaputiei North', 'Kaputiei North'), ('Karen', 'Karen'),
                                                        ('Kariobangi South', 'Kariobangi South'),
                                                        ('Karioboangi North', 'Karioboangi North'),
                                                        ('Karura', 'Karura'), ('Kasarani', 'Kasarani'),
                                                        ('Kawangware', 'Kawangware'),
                                                        ('Kayole Central', 'Kayole Central'),
                                                        ('Kayole North', 'Kayole North'),
                                                        ('Kayole South', 'Kayole South'),
                                                        ('Keekonyokie', 'Keekonyokie'),
                                                        ('Kenyawa-poka', 'Kenyawa-poka'), ('Kiamaiko', 'Kiamaiko'),
                                                        ('Kileleshwa', 'Kileleshwa'), ('Kilimani', 'Kilimani'),
                                                        ('Kimana', 'Kimana'), ('Kitengela', 'Kitengela'),
                                                        ('Kitisuru', 'Kitisuru'), ('Komarock', 'Komarock'),
                                                        ('Korogocho', 'Korogocho'), ('Kuku', 'Kuku'),
                                                        ('Kwa Njenga', 'Kwa Njenga'), ('Kwa Rueben', 'Kwa Rueben'),
                                                        ('Kware', 'Kware'), ('Laini Saba', 'Laini Saba'),
                                                        ('Landimawe', 'Landimawe'), ('Lindi', 'Lindi'),
                                                        ('Lower Savannah', 'Lower Savannah'),
                                                        ('Lucky Summer', 'Lucky Summer'), ('Mabatini', 'Mabatini'),
                                                        ('Magadi', 'Magadi'),
                                                        ("MakinaSarang'ombe", "MakinaSarang'ombe"),
                                                        ('Makongeni', 'Makongeni'), ('Maringo/Hamza', 'Maringo/Hamza'),
                                                        ('Maringo/Hamza', 'Maringo/Hamza'),
                                                        ('Matapato North', 'Matapato North'),
                                                        ('Matapato South', 'Matapato South'),
                                                        ('Mathare North', 'Mathare North'),
                                                        ('Matopeni/Spring Valley', 'Matopeni/Spring Valley'),
                                                        ('Mihango', 'Mihango'), ('Mosiro', 'Mosiro'),
                                                        ('Mountain View', 'Mountain View'), ('Mowlem', 'Mowlem'),
                                                        ('Mugumo-ini', 'Mugumo-ini'), ('Mutu-Ini', 'Mutu-Ini'),
                                                        ('Mwiki', 'Mwiki'), ('Nairobi Central', 'Nairobi Central'),
                                                        ('Nairobi South', 'Nairobi South'),
                                                        ('Nairobi West', 'Nairobi West'), ('Ngando', 'Ngando'),
                                                        ('Ngara', 'Ngara'), ('Ngei', 'Ngei'), ('Ngong', 'Ngong'),
                                                        ('Njiru', 'Njiru'), ('Nkaimurunya', 'Nkaimurunya'),
                                                        ('Nyayo Highrise', 'Nyayo Highrise'), ('Olkeri', 'Olkeri'),
                                                        ('Oloolua', 'Oloolua'),
                                                        ('Oloosirkon/Sholinke', 'Oloosirkon/Sholinke'),
                                                        ('Ongata Rongai', 'Ongata Rongai'), ('Pangani', 'Pangani'),
                                                        ('Parklands/Highridge', 'Parklands/Highridge'),
                                                        ('Pipeline', 'Pipeline'), ('Pumwani', 'Pumwani'),
                                                        ('Purko', 'Purko'), ('Riruta', 'Riruta'), ('Rombo', 'Rombo'),
                                                        ('Roysambu', 'Roysambu'), ('Ruai', 'Ruai'),
                                                        ('South C', 'South C'), ('Umoja I', 'Umoja I'),
                                                        ('Umoja II', 'Umoja II'), ('Upper Savannah', 'Upper Savannah'),
                                                        ('Utalii', 'Utalii'), ('Utawala', 'Utawala'),
                                                        ('Uthiru/Ruthimitu', 'Uthiru/Ruthimitu'),
                                                        ('Viwandani', 'Viwandani'), ('Waithaka', 'Waithaka'), (
                                                        'Woodley/Kenyatta Golf Course', 'Woodley/Kenyatta Golf Course'),
                                                        ('Zimmerman', 'Zimmerman'),
                                                        ('Ziwani/Kariokor', 'Ziwani/Kariokor')],
                                   max_length=64,
                                   null=True),
        ),
    ]
