# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('rosevrobank', '0005_fill_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rosevrobankorder',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='UUID', db_index=True),
        ),
    ]
