# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Listing',
            fields=[
                ('tx_id', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('category', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('subcategory', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('quantity', models.IntegerField(default=0, null=True, blank=True)),
                ('requested_peercoin', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('peercoin_address', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('block_number_created', models.IntegerField(default=0, null=True, blank=True)),
                ('time_created', models.IntegerField(default=0, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Listing',
                'verbose_name_plural': 'Listings',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('tx_id', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('listing_tx_id', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('offer_tx_id', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('peercoin_address', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('message', models.TextField(null=True, blank=True)),
                ('block_number_created', models.IntegerField(default=0, null=True, blank=True)),
                ('time_created', models.IntegerField(default=0, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
            },
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('tx_id', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('listing_tx_id', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('quantity', models.IntegerField(default=0, null=True, blank=True)),
                ('offered_peercoin', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('peercoin_address', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('block_number_created', models.IntegerField(default=0, null=True, blank=True)),
                ('time_created', models.IntegerField(default=0, null=True, blank=True)),
                ('offer_status', models.IntegerField(default=1, null=True, blank=True)),
                ('tx_id_status_change', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('block_number_status_change', models.IntegerField(default=0, null=True, blank=True)),
                ('time_status_change', models.IntegerField(default=0, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Offer',
                'verbose_name_plural': 'Offers',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('tx_id', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('block_number_created', models.IntegerField(default=0, null=True, blank=True)),
                ('time_created', models.IntegerField(default=0, null=True, blank=True)),
                ('peercoin_address', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('payload_retrieved', models.BooleanField(default=False)),
                ('payload_executed', models.BooleanField(default=False)),
                ('pm_key', models.CharField(default=b'', max_length=255, null=True, db_index=True, blank=True)),
                ('pm_payload', models.TextField(null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Transaction',
                'verbose_name_plural': 'Transactions',
            },
        ),
    ]
