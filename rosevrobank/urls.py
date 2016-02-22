from django.conf.urls import url, include

from rosevrobank.views import ProcessPaymentView, PaymentSuccessView, PaymentFailView

urlpatterns = [
    url('^payment/', include([
        url('^process/(?P<order_id>\d+)/$', ProcessPaymentView.as_view(), name='rosevrobank-payment-process'),
        url('^success/(?P<order_id>\d+)/$', PaymentSuccessView.as_view(), name='rosevrobank-payment-success'),
        url('^fail/(?P<order_id>\d+)/$', PaymentFailView.as_view(), name='rosevrobank-payment-fail'),
    ]))
]
