from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel


class RosEvroBankOrder(TimeStampedModel, models.Model):
    order_content_type = models.ForeignKey(ContentType)
    order_object_id = models.IntegerField()
    order = GenericForeignKey('order_content_type', 'order_object_id')
    reb_order_id = models.CharField(_('RosEvroBank order id'), max_length=255, db_index=True)

    class Meta(object):
        verbose_name = _('RosEvroBank order')
        verbose_name_plural = _('RosEvroBank orders')
        ordering = ('-id', )
