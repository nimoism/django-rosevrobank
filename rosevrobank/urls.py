from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.conf.urls import url, include

from rosevrobank.views import ProcessPaymentView, PaymentSuccessView, PaymentFailView

id_pattern = settings.ROSEVROBANK_SOURCE_ID_URL_REGEX

urlpatterns = [
    url('^payment/', include([
        url('^process/(?P<source_id>%s)/$' % id_pattern, ProcessPaymentView.as_view(),
            name='rosevrobank-payment-process'),
        url('^success/(?P<uuid>%s)/$' % id_pattern, PaymentSuccessView.as_view(),
            name='rosevrobank-payment-success'),
        url('^fail/(?P<uuid>%s)/$' % id_pattern, PaymentFailView.as_view(),
            name='rosevrobank-payment-fail'),
    ]))
]
