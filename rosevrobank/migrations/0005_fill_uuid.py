# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import migrations, models


def gen_uuid(apps, schema_editor):
    MyModel = apps.get_model('rosevrobank', 'RosEvroBankOrder')
    for row in MyModel.objects.all():
        row.uuid = uuid.uuid4()
        row.save()


class Migration(migrations.Migration):

    dependencies = [
        ('rosevrobank', '0004_auto_20160609_2307'),
    ]

    operations = [
        migrations.RunPython(gen_uuid, migrations.RunPython.noop)
    ]
