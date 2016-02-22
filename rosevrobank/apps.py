from importlib import import_module
from django.apps.config import AppConfig

import_module('rosevrobank.conf')


class RosEvroBankAppConfig(AppConfig):
    name = 'rosevrobank'
