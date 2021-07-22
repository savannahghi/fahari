# Generated by Django 3.2.5 on 2021-07-22 12:38

from django.db import migrations

EXTENSIONS_SQL = '''
CREATE EXTENSION IF NOT EXISTS plpgsql;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_raster;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
-- CREATE EXTENSION IF NOT EXISTS postgis_sfcgal;
-- CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
-- CREATE EXTENSION IF NOT EXISTS address_standardizer;
-- CREATE EXTENSION IF NOT EXISTS address_standardizer_data_us;
-- CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;
'''

class Migration(migrations.Migration):

    dependencies = [
        ('common', '0012_auto_20210722_1525'),
    ]

    operations = [
        migrations.RunSQL(EXTENSIONS_SQL)
    ]
