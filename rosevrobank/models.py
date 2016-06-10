from __future__ import absolute_import, unicode_literals

import uuid

from django.apps.registry import apps
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields.json import JSONField
from django_extensions.db.models import TimeStampedModel

from rosevrobank.client import client
from rosevrobankapi.client import RosEvroBankClient


class RosEvroBankOrder(TimeStampedModel, models.Model):
    STATUS_CHOICES = (
        (RosEvroBankClient.ORDER_STATUS_REGISTERED, _('order is registered but not paid for')),
        (RosEvroBankClient.ORDER_STATUS_PRE_AUTH_HOLD, _('pre authorized amount held')),
        (RosEvroBankClient.ORDER_STATUS_AUTHORIZED, _('order amount authorization completed')),
        (RosEvroBankClient.ORDER_STATUS_AUTH_CANCELLED, _('authorization cancelled')),
        (RosEvroBankClient.ORDER_STATUS_REFUNDED, _('refund operation to transaction carried out')),
        (RosEvroBankClient.ORDER_STATUS_ACS_AUTH_INITIATED, _('ACS authorization initiated')),
        (RosEvroBankClient.ORDER_STATUS_AUTH_REJECTED, _('authorization rejected')),
    )

    source_content_type = models.ForeignKey(ContentType)
    source_object_id = models.IntegerField()
    source = GenericForeignKey('source_content_type', 'source_object_id')
    uuid = models.UUIDField(_('UUID'), default=uuid.uuid4, db_index=True, unique=True)
    reb_order_id = models.CharField(_('RosEvroBank order id'), max_length=255, blank=True, null=True, db_index=True,
                                    unique=True)
    reb_order_data = JSONField(blank=True, null=True)
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, blank=True, null=True)

    @classmethod
    def get_by_source(cls, source):
        """
        Gets RosEvroBankOrder by project source object

        :param source: source object
        :type: django.db.models.Model
        :return: RosEvroBankOrder object
        :rtype: RosEvroBankOrder
        """
        return cls.get_last(source)

    def save(self, **kwargs):
        self.full_clean()
        super(RosEvroBankOrder, self).save(**kwargs)

    def clean(self):
        super(RosEvroBankOrder, self).clean()
        if not self.pk and not self.can_create(self.source):
            raise ValidationError("Cannot create order when previous is not finished")

    @classmethod
    def get_last(cls, source):
        source_ct = ContentType.objects.get_for_model(source)
        last_reb_order = cls.objects.filter(source_content_type=source_ct, source_object_id=source.id)\
            .order_by('-created', '-id').first()
        return last_reb_order

    @classmethod
    def can_create(cls, source):
        prev_reb_order = cls.get_last(source)
        return not (prev_reb_order and prev_reb_order.status in (
            None,
            RosEvroBankClient.ORDER_STATUS_REGISTERED,
            RosEvroBankClient.ORDER_STATUS_AUTHORIZED,
        ))

    def clean_fields(self, exclude=None):
        super(RosEvroBankOrder, self).clean_fields(exclude=exclude)
        self._validate_requires()

    def _validate_requires(self):
        if (self.status is None) is not (self.reb_order_id is None):
            raise ValidationError({'reb_order_id': 'status and reb_order_id must be set both'})

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


def get_source_model():
    """
    Returns project order model
    :return: order model
    :rtype: django.db.models.Model
    """
    model_name = settings.ROSEVROBANK_SOURCE_MODEL
    app_label, model_name = model_name.split('.')
    model = apps.get_app_config(app_label).get_model(model_name)
    return model

source_model = get_source_model()
