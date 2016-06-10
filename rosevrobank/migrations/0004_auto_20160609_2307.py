# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('rosevrobank', '0003_auto_20160609_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='rosevrobankorder',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, null=True, verbose_name='UUID', db_index=True),
        ),
        migrations.AlterField(
            model_name='rosevrobankorder',
            name='reb_order_id',
            field=models.CharField(null=True, max_length=255, blank=True, unique=True, verbose_name='RosEvroBank order id', db_index=True),
        ),
        migrations.AlterField(
            model_name='rosevrobankorder',
            name='status',
            field=models.IntegerField(blank=True, null=True, verbose_name='status', choices=[(0, 'order is registered but not paid for'), (1, 'pre authorized amount held'), (2, 'order amount authorization completed'), (3, 'authorization cancelled'), (4, 'refund operation to transaction carried out'), (5, 'ACS authorization initiated'), (6, 'authorization rejected')]),
        ),
    ]
