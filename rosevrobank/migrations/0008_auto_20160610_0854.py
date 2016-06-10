# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    dependencies = [
        ('rosevrobank', '0007_rosevrobankorder_reb_order_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rosevrobankorder',
            name='reb_order_data',
            field=django_extensions.db.fields.json.JSONField(null=True, blank=True),
        ),
    ]
