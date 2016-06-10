# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    dependencies = [
        ('rosevrobank', '0006_auto_20160609_2317'),
    ]

    operations = [
        migrations.AddField(
            model_name='rosevrobankorder',
            name='reb_order_data',
            field=django_extensions.db.fields.json.JSONField(null=True),
        ),
    ]
