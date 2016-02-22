from django.conf import settings
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.views.generic.base import TemplateView, View

from rosevrobank.client import client
from rosevrobank.models import RosEvroBankOrder, order_model
from rosevrobankapi.response import BaseErrorResponse


class ClientViewMixin(object):
    @property
    def client(self):
        if not hasattr(self, '_client'):
            setattr(self, '_client', client)
        return getattr(self, '_client')


class OrderViewMixin(object):

    def get_order_id(self):
        return self.kwargs.get('order_id')

    def get_order(self):
        order_id = self.get_order_id()
        order = order_model._default_manager.get(id=order_id)
        return order


class ProcessPaymentView(ClientViewMixin, OrderViewMixin, View):
    success_url = None
    fail_url = None

    def process(self, order):
        try:
            result = self.client.register_order(
                order_number=order.id,
                amount=order.get_total_price(),
                result_url=self.get_success_url(order),
                fail_url=self.get_fail_url(order),
            )
        except BaseErrorResponse as result:
            return self.fail(order, result)
        else:
            return self.success(order, result)

    def get_success_url(self, order):
        url = self.success_url or settings.ROSEVROBANK_PAYMENT_SUCCESS_URL or \
              reverse(settings.ROSEVROBANK_PAYMENT_SUCCESS_VIEW, kwargs={'order_id': order.id})
        return url

    def get_fail_url(self, order):
        url = self.fail_url or settings.ROSEVROBANK_PAYMENT_FAIL_URL or \
              reverse(settings.ROSEVROBANK_PAYMENT_FAIL_VIEW, kwargs={'order_id': order.id})
        return url

    def success(self, order, result):
        reb_order_id = result.order_id
        reb_order = RosEvroBankOrder(
            reb_order_id=reb_order_id,
            order=order,
            status=self.client.get_order_status_value(reb_order_id)
        )
        reb_order.save()
        form_url = result.form_url
        return HttpResponseRedirect(form_url)

    def fail(self, order, result):
        pass

    def get(self, request, *args, **kwargs):
        order = self.get_order()
        return self.process(order)


class BasePaymentResultView(OrderViewMixin, TemplateView):
    context_order_name = 'order'
    context_reb_order_name = 'reb_order'

    def get_reb_order(self):
        order = self.get_order()
        reb_order = RosEvroBankOrder.get_by_order(order)
        return reb_order

    def get_context_data(self, **kwargs):
        kwargs = super(BasePaymentResultView, self).get_context_data(**kwargs)
        reb_order = self.get_reb_order()
        kwargs.update({
            self.context_order_name: reb_order.order,
            self.context_reb_order_name: reb_order,
        })
        return kwargs


class PaymentSuccessView(BasePaymentResultView):
    template_name = 'rosevrobank/success.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        reb_order = context[self.context_reb_order_name]
        reb_order.update_status()
        return self.render_to_response(context)


class PaymentFailView(BasePaymentResultView):
    template_name = 'rosevrobank/fail.html'
