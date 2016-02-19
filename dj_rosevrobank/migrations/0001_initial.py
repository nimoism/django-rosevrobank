# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='RosEvroBankOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order_object_id', models.IntegerField()),
                ('reb_order_id', models.CharField(max_length=255, verbose_name='RosEvroBank order id', db_index=True)),
                ('order_content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('-id',),
                'verbose_name': 'RosEvroBank order',
                'verbose_name_plural': 'RosEvroBank orders',
            },
        ),
    ]
