# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rosevrobank', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rosevrobankorder',
            name='status',
            field=models.IntegerField(default=0, verbose_name='status', choices=[(0, 'registered'), (1, 'preauthorization hold'), (2, 'authorized'), (3, 'authorization cancelled'), (4, 'refunded'), (5, 'ACS authrization initiated'), (6, 'authorization rejected')]),
        ),
        migrations.AlterField(
            model_name='rosevrobankorder',
            name='reb_order_id',
            field=models.CharField(unique=True, max_length=255, verbose_name='RosEvroBank order id', db_index=True),
        ),
    ]
