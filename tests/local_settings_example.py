# coding: utf-8
from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy

PAYMASTER_PASSWORD = 'FOR CHECK NOTIFICATION'
PAYMASTER_MERCHANT_ID = 'YOUR MERCHANT_ID'

PAYMASTER_API_AUTH = {
    'LOGIN': 'test_2@example.com',
    'PASSWORD': 'example',
}


PAYMASTER_INIT_URL = reverse_lazy('paymaster:test')
PAYMASTER_PAYER_ENCODER_CLASS = 'paymaster.payer.RawPayerEncoder'
