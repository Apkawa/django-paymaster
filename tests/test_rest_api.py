# coding: utf-8

from __future__ import unicode_literals

try:
    from httplib import HTTPConnection
except ImportError:
    from http.client import HTTPConnection

import logging
from unittest import TestCase

try:
    from unittest import mock
except ImportError:
    import mock

from django.conf import settings

from paymaster.rest_api.client import PaymasterApiClient


def log_requests():
    HTTPConnection.debuglevel = 1
    logging.basicConfig()  # you need to initialize logging, otherwise you will not see anything from requests
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


class ApiTest(TestCase):
    def setUp(self):
        PaymasterApiClient._gen_nonce = mock.MagicMock(return_value='ttt')
        self.client = PaymasterApiClient(login='TestLogin')
        self.payment_id = '43149010'
        self.invoice_id = '43636-20160125-14968c91'

    def test_get_payment(self):
        result = self.client.get_payment(self.payment_id)
        assert result

    def test_get_payment_by_invoice_id(self):
        result = self.client.get_payment_by_invoice_id(
            self.invoice_id,
            merchant_id=settings.PAYMASTER_MERCHANT_ID,
        )
        assert result

    def test_get_payments(self):
        result = self.client.get_payments(
            period_from='2016-01-01',
            period_to='2016-01-25',
        )
        assert result

    def test_refund(self):
        result = self.client.refund_payment(self.payment_id, amount=56)
        assert result

    def test_list_refund(self):
        result = self.client.list_refunds()
        assert result

    def test_confirm_payment(self):
        result = self.client.confirm_payment(self.payment_id)
        assert result

    def test_cancel_payment(self):
        result = self.client.cancel_payment(self.payment_id)
        assert result
