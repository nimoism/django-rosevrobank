from __future__ import absolute_import, unicode_literals

from django.dispatch.dispatcher import Signal


rosevrobank_payment_request_fail = Signal(providing_args=['reb_order', 'error_response'])

rosevrobank_pre_payment = Signal(providing_args=['reb_order', 'reb_result'])

rosevrobank_payment_result_success = Signal(providing_args=['reb_order', 'reb_result'])

rosevrobank_payment_result_fail = Signal(providing_args=['reb_order', 'reb_result'])
