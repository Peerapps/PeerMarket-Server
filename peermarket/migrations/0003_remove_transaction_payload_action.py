# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('peermarket', '0002_transaction_payload_action'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='payload_action',
        ),
    ]
