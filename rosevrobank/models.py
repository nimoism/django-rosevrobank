from django.apps.registry import apps
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from rosevrobank.client import client
from rosevrobankapi.client import RosEvroBankClient


class RosEvroBankOrder(TimeStampedModel, models.Model):
    STATUS_CHOICES = (
        (RosEvroBankClient.ORDER_STATUS_REGISTERED, _('registered')),
        (RosEvroBankClient.ORDER_STATUS_PRE_AUTH_HOLD, _('preauthorization hold')),
        (RosEvroBankClient.ORDER_STATUS_AUTHORIZED, _('authorized')),
        (RosEvroBankClient.ORDER_STATUS_AUTH_CANCELLED, _('authorization cancelled')),
        (RosEvroBankClient.ORDER_STATUS_REFUNDED, _('refunded')),
        (RosEvroBankClient.ORDER_STATUS_ACS_AUTH_INITIATED, _('ACS authrization initiated')),
        (RosEvroBankClient.ORDER_STATUS_AUTH_REJECTED, _('authorization rejected')),
    )

    order_content_type = models.ForeignKey(ContentType)
    order_object_id = models.IntegerField()
    order = GenericForeignKey('order_content_type', 'order_object_id')
    reb_order_id = models.CharField(_('RosEvroBank order id'), max_length=255, db_index=True, unique=True)
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=RosEvroBankClient.ORDER_STATUS_REGISTERED)

    @property
    def client(self):
        if not hasattr(self, '_client'):
            setattr(self, '_client', client)
        return getattr(self, '_client')

    def update_status(self, save=True):
        self.status = self.client.get_order_status_value(self.reb_order_id)
        if save:
            self.save(update_fields=['status'])

    class Meta(object):
        verbose_name = _('RosEvroBank order')
        verbose_name_plural = _('RosEvroBank orders')
        ordering = ('-id', )


def get_order_model():
    """
    Returns project order model
    :return: order model
    :rtype: django.db.models.Model
    """
    model_name = settings.ROSEVROBANK_PROJECT_ORDER_MODEL
    app_label, model_name = model_name.split('.')
    model = apps.get_app_config(app_label).get_model(model_name)
    return model

order_model = get_order_model()
