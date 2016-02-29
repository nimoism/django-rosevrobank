from importlib import import_module
from django.conf import settings

from rosevrobankapi.client import RosEvroBankClient


def get_backend(backend_path, options=None):
    backend_module_name, backend_class_name = backend_path.rsplit('.', 1)
    backend_module = import_module(backend_module_name)
    backend_class = getattr(backend_module, backend_class_name)
    options = options or settings.ROSEVROBANK_BACKEND_OPTIONS.get(backend_class.name, {})
    backend = backend_class(**options)
    return backend


class RosEvroBankClientProxy(object):

    def __init__(self, api_client):
        self.client = api_client

    def __getattr__(self, item):
        return getattr(self.client, item)

    def get_order_status_value(self, reb_order_id, **kwargs):
        """
        :param reb_order_id: RosEvroBank order id
        :type reb_order_id: str
        :return: order status value
        :rtype: int
        """
        response = self.client.get_order_status(reb_order_id, **kwargs)
        order_status = response.order_status
        return order_status


def get_client(**kwargs):
    """
    :param kwargs: options for API client
    :return: RosEvroBank proxy client
    :rtype: RosEvroBankClientProxy
    """
    kwargs.setdefault('backend', get_backend(settings.ROSEVROBANK_BACKEND))
    api_client = RosEvroBankClient(**kwargs)
    return RosEvroBankClientProxy(api_client)

client = get_client()
