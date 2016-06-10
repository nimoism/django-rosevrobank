# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rosevrobank', '0002_auto_20160222_1317'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rosevrobankorder',
            old_name='order_content_type',
            new_name='source_content_type',
        ),
        migrations.RenameField(
            model_name='rosevrobankorder',
            old_name='order_object_id',
            new_name='source_object_id',
        ),
        migrations.AlterField(
            model_name='rosevrobankorder',
            name='status',
            field=models.IntegerField(default=0, verbose_name='status', choices=[(0, 'order is registered but not paid for'), (1, 'pre authorized amount held'), (2, 'order amount authorization completed'), (3, 'authorization cancelled'), (4, 'refund operation to transaction carried out'), (5, 'ACS authorization initiated'), (6, 'authorization rejected')]),
        ),
    ]
