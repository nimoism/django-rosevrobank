import os
from logging import getLogger

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, Http404, HttpResponse
from django.template import loader
from django.template.context import RequestContext
from django.views.generic.base import TemplateView, View

from rosevrobank.client import client
from rosevrobank.models import RosEvroBankOrder, order_model
from rosevrobankapi.client import RosEvroBankClient
from rosevrobankapi.response import BaseErrorResponse, HttpErrorResponse, ApplicationErrorResponse

logger = getLogger(__name__)


class ClientViewMixin(object):
    remote_error_template = "rosevrobank/client_error.html"
    remote_http_error_template = "rosevrobank/client_http_error.html"

    user_errors = (
        RosEvroBankClient.ERROR_NO_ERROR,
        RosEvroBankClient.ERROR_REGISTERED_ALREADY,
    )

    @property
    def client(self):
        if not hasattr(self, '_client'):
            setattr(self, '_client', client)
        return getattr(self, '_client')

    def client_error_response(self, request, response, **extra_context):
        if isinstance(response, HttpErrorResponse):
            return self.client_http_error_response(request, response, **extra_context)
        elif isinstance(response, ApplicationErrorResponse):
            user_error = response.code in self.user_errors
            extra_context.update(user_error=user_error)
            return self.client_app_error_response(request, response, **extra_context)

    @classmethod
    def _get_template_names(cls, base_template, prefix=None, action_name=None):
        template_names = []
        dir_name, file_name = os.path.split(base_template)
        name, ext = os.path.splitext(file_name)
        if prefix:
            if action_name:
                template_names.append(os.path.join(dir_name, prefix + '_' + name + '_' + action_name + ext))
            template_names.append(os.path.join(dir_name, prefix + '_' + name + ext))
        if action_name:
            template_names.append(os.path.join(dir_name, name + '_' + action_name + ext))
        template_names.append(base_template)
        return template_names

    def _client_error_response(self, template_name, request, response, prefix=None, action_name=None, **extra_context):
        context = RequestContext(request, {'response': response})
        context.update(extra_context)
        template = loader.select_template(self._get_template_names(template_name, prefix=prefix,
                                                                   action_name=action_name))
        return HttpResponse(template.render(context))

    def client_app_error_response(self, request, response, prefix=None, action_name=None, **extra_context):
        return self._client_error_response(self.remote_error_template, request, response, prefix, action_name,
                                           **extra_context)

    def client_http_error_response(self, request, response, prefix=None, action_name=None, **extra_context):
        return self._client_error_response(self.remote_http_error_template, request, response, prefix, action_name,
                                           **extra_context)


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
                return_url=self.get_success_url(order),
                fail_url=self.get_fail_url(order),
            )
        except BaseErrorResponse as result:
            return self.fail(order, result)
        else:
            return self.success(order, result)

    def _build_absolute_uri(self, url):
        return self.request.build_absolute_uri(url)

    def get_success_url(self, order):
        url = self.success_url or settings.ROSEVROBANK_PAYMENT_SUCCESS_URL or \
              reverse(settings.ROSEVROBANK_PAYMENT_SUCCESS_VIEW, kwargs={'order_id': order.id})
        return self._build_absolute_uri(url)

    def get_fail_url(self, order):
        url = self.fail_url or settings.ROSEVROBANK_PAYMENT_FAIL_URL or \
              reverse(settings.ROSEVROBANK_PAYMENT_FAIL_VIEW, kwargs={'order_id': order.id})
        return self._build_absolute_uri(url)

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
        return self.client_error_response(self.request, result, prefix='payment', action_name='register_order',
                                          **{'order': order})

    def get(self, request, *args, **kwargs):
        order = self.get_order()
        return self.process(order)


class BasePaymentResultView(ClientViewMixin, OrderViewMixin, TemplateView):
    context_order_name = 'order'
    context_reb_order_name = 'reb_order'
    client_error_prefix = None

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        order = context[self.context_order_name]
        reb_order = context[self.context_reb_order_name]
        reb_order_id = request.GET.get('orderId')
        if reb_order.reb_order_id != reb_order_id:
            raise Http404()
        try:
            order_status = self.client.get_order_status_value(reb_order.reb_order_id)
        except BaseErrorResponse as response:
            return self.client_error_response(request, response, prefix=self.client_error_prefix,
                                              action_name='get_order_status', **{'order': order})
        else:
            reb_order.status = order_status
            reb_order.save(update_fields=['status'])
        return self.render_to_response(context)

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
    template_name = 'rosevrobank/payment_success.html'
    client_error_prefix = 'payment_success'


class PaymentFailView(BasePaymentResultView):
    template_name = 'rosevrobank/payment_fail.html'
    client_error_prefix = 'payment_fail'
