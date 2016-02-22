from appconf.base import AppConf


class RosEvroBankConf(AppConf):
    TEST = False
    CLIENT_RAISE_ERRORS = False

    AUTH_USER_NAME = None
    AUTH_PASSWORD = None
    BACKEND = 'rosevrobankapi.backends.rest.backend.RestBackend'
    BACKEND_OPTIONS = {}

    PAYMENT_SUCCESS_VIEW = 'rosevrobank-payment-success'
    PAYMENT_FAIL_VIEW = 'rosevrobank-payment-fail'
    PAYMENT_SUCCESS_URL = None
    PAYMENT_FAIL_URL = None

    def configure(self):
        for backend_name in ('rest', 'soap'):
            if backend_name not in self.configured_data['BACKEND_OPTIONS']:
                self.configured_data['BACKEND_OPTIONS'][backend_name] = {}
            self.configured_data['BACKEND_OPTIONS'][backend_name].update({
                'user_name': self.configured_data['AUTH_USER_NAME'],
                'password': self.configured_data['AUTH_PASSWORD'],
                'test': self.configured_data['TEST'],
            })
        return self.configured_data

    class Meta(object):
        prefix = 'rosevrobank'
