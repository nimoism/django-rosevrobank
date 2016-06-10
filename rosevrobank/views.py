from __future__ import absolute_import, unicode_literals

import json

import os
from logging import getLogger

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, Http404, HttpResponse
from django.template import loader
from django.template.context import RequestContext
from django.views.generic.base import TemplateView, View

from rosevrobank import signals
from rosevrobank.client import client
from rosevrobank.models import RosEvroBankOrder, source_model
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

    def get_source_id(self):
        return self.kwargs.get('source_id')

    def get_source(self):
        source_id = self.get_source_id()
        source = source_model._default_manager.get(**{
            settings.ROSEVROBANK_SOURCE_ID_FIELD: source_id
        })
        return source

    def get_reb_order_uuid(self):
        return self.kwargs.get('uuid')

    def get_reb_order(self):
        reb_order_uuid = self.get_reb_order_uuid()
        reb_order = RosEvroBankOrder.objects.get(uuid=reb_order_uuid)
        return reb_order


class ProcessPaymentView(ClientViewMixin, OrderViewMixin, View):
    success_url = None
    fail_url = None

    def get(self, request, *args, **kwargs):
        source = self.get_source()
        if source.get_amount_for_pay() > 0:
            return self.process(source)
        else:
            reb_order = RosEvroBankOrder.get_last(source)
            if reb_order.status == RosEvroBankClient.ORDER_STATUS_AUTHORIZED:
                return HttpResponseRedirect(self.get_success_url(reb_order) + '?orderId=' + reb_order.reb_order_id)
            else:
                raise RuntimeError('Amount for pay is %s' % source.get_amount_for_pay())

    def process(self, source):
        last_reb_order = RosEvroBankOrder.get_last(source)
        if last_reb_order:
            try:
                order_status = self.client.get_order_status_value(last_reb_order.reb_order_id)
            except BaseErrorResponse as result:
                return self.fail(last_reb_order, result)
            else:
                if order_status != last_reb_order.status:
                    last_reb_order.status = order_status
                    last_reb_order.save(update_fields=['status'])
        if RosEvroBankOrder.can_create(source):
            reb_order = RosEvroBankOrder(source=source)
            reb_order.save()
        elif last_reb_order:
            if last_reb_order.status == RosEvroBankClient.ORDER_STATUS_REGISTERED:
                reb_order = last_reb_order
                if reb_order.reb_order_data:
                    reb_order_data = reb_order.reb_order_data
                    form_url = reb_order_data.get('form_url')
                    if form_url:
                        return HttpResponseRedirect(form_url)
                return HttpResponseRedirect(self.get_fail_url(reb_order) + '?orderId=' + reb_order.reb_order_id)
            elif last_reb_order.status == RosEvroBankClient.ORDER_STATUS_AUTHORIZED:
                reb_order = last_reb_order
                return HttpResponseRedirect(self.get_success_url(reb_order) + '?orderId=' + reb_order.reb_order_id)
            else:
                raise RuntimeError('Wrong REB orders states')
        else:
            raise RuntimeError('Wrong REB orders states')
        try:
            result = self.client.register_order(
                order_number=reb_order.uuid.hex,
                amount=source.get_amount_for_pay(),
                return_url=self.get_success_url(reb_order),
                fail_url=self.get_fail_url(reb_order),
                session_timeout=30,
            )
        except BaseErrorResponse as result:
            return self.fail(reb_order, result)
        else:
            return self.success(reb_order, result)

    def _build_absolute_uri(self, url):
        return self.request.build_absolute_uri(url)

    def get_success_url(self, reb_order):
        url = self.success_url or settings.ROSEVROBANK_PAYMENT_SUCCESS_URL or \
            reverse(settings.ROSEVROBANK_PAYMENT_SUCCESS_VIEW, kwargs={'uuid': reb_order.uuid})
        return self._build_absolute_uri(url)

    def get_fail_url(self, reb_order):
        url = self.fail_url or settings.ROSEVROBANK_PAYMENT_FAIL_URL or \
            reverse(settings.ROSEVROBANK_PAYMENT_FAIL_VIEW, kwargs={'uuid': reb_order.uuid})
        return self._build_absolute_uri(url)

    def success(self, reb_order, result):
        reb_order_id = result.order_id
        reb_order.reb_order_id = reb_order_id
        reb_order.status = self.client.get_order_status_value(reb_order_id)
        reb_order.save()
        reb_order.reb_order_data = json.dumps(result.data)
        reb_order.save()
        form_url = result.form_url
        signals.rosevrobank_pre_payment.send(self.__class__, reb_order=reb_order, reb_result=result)
        return HttpResponseRedirect(form_url)

    def fail(self, reb_order, result):
        response = self.client_error_response(self.request, result, prefix='payment', action_name='register_order',
                                              **{'reb_order': reb_order})
        signals.rosevrobank_payment_request_fail.send(self.__class__, reb_order=reb_order, error_response=result)
        return response


class BasePaymentResultView(ClientViewMixin, OrderViewMixin, TemplateView):
    context_source_name = 'source'
    context_reb_order_name = 'reb_order'
    client_error_prefix = None

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        reb_order = context[self.context_reb_order_name]
        reb_order_id = request.GET.get('orderId')
        if reb_order.reb_order_id != reb_order_id:
            raise Http404()
        try:
            response = self.client.get_order_status(reb_order.reb_order_id)
        except BaseErrorResponse as response:
            response = self.client_error_response(request, response, prefix=self.client_error_prefix,
                                                  action_name='get_order_status', **{'reb_order': reb_order})
            signals.rosevrobank_payment_request_fail.send(self.__class__, reb_order=reb_order, error_response=response)
            return response
        else:
            order_status = response.order_status
            reb_order.status = order_status
            reb_order.save(update_fields=['status'])
            if order_status == RosEvroBankClient.ORDER_STATUS_AUTHORIZED:
                signals.rosevrobank_payment_result_success.send(self.__class__, reb_order=reb_order, reb_result=response)
            else:
                signals.rosevrobank_payment_result_fail.send(self.__class__, reb_order=reb_order, reb_result=response)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        kwargs = super(BasePaymentResultView, self).get_context_data(**kwargs)
        reb_order = self.get_reb_order()
        kwargs.update({
            self.context_source_name: reb_order.source,
            self.context_reb_order_name: reb_order,
        })
        return kwargs


class PaymentSuccessView(BasePaymentResultView):
    template_name = 'rosevrobank/payment_success.html'
    client_error_prefix = 'payment_success'


class PaymentFailView(BasePaymentResultView):
    template_name = 'rosevrobank/payment_fail.html'
    client_error_prefix = 'payment_fail'
