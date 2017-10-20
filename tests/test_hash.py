# coding: utf-8
from __future__ import unicode_literals

from unittest import TestCase

from paymaster import settings

from paymaster.utils import calculate_hash

from paymaster.compat import urlparse


class TestCalculateHash(TestCase):
    def test_hash_prod(self):
        qs = {'LMI_CURRENCY': 'RUB',
              'LMI_HASH': 'DL6N55OGh/c+AzkW/oagf8e1JfquTSWacWQ+JzEUKSI=',
              'LMI_MERCHANT_ID': 'ebc4f3fe-d395-4e08-a4ef-81ca6f4e04a6',
              'LMI_PAID_AMOUNT': '80.00',
              'LMI_PAID_CURRENCY': 'RUB',
              'LMI_PAYER_IDENTIFIER': '5XXXXXXXXXXX1756',
              'LMI_PAYMENT_AMOUNT': '80.00',
              'LMI_PAYMENT_DESC': '\xd0\x9f\xd1\x80\xd0\xb5\xd0\xb4\xd0\xbe\xd0\xbf\xd0\xbb\xd0\xb0\xd1\x82\xd0\xb0 \xd0\xb7\xd0\xb0 \xd0\xb7\xd0\xb0\xd0\xba\xd0\xb0\xd0\xb7 \xe2\x84\x9643636 203108. \xd0\x9f\xd1\x80\xd0\xbe\xd0\xba\xd0\xb0\xd1\x82 \xd1\x81\xd1\x82\xd1\x83\xd0\xbb\xd0\xb0 \xd0\x94\xd0\xb6\xd0\xb5\xd1\x84',
              'LMI_PAYMENT_METHOD': 'BankCard',
              'LMI_PAYMENT_NO': '43636-20160125-14968c91',
              'LMI_PAYMENT_REF': '602517972679',
              'LMI_PAYMENT_SYSTEM': '93',
              'LMI_SYS_PAYMENT_DATE': '2016-01-25T16:26:29',
              'LMI_SYS_PAYMENT_ID': '43149010',
              'LOC_PAYER_ID': 'c2MAAvKGau4PdTiB6jV1kCh1ZcLkZWg7PhWQESVm+Zpn2h+KMbJ1Sd26NQFEhs9RMtSmc6XPupIo\n75SOwOa6OXTx3stbnYE+MOKg2LFqpd5MT1xdW5SD',
              'order': '43636',
              'payment_type': 'BankCard'}

        qs = "LMI_MERCHANT_ID=ebc4f3fe-d395-4e08-a4ef-81ca6f4e04a6" \
             "&LMI_PAYMENT_SYSTEM=93&LMI_CURRENCY=RUB" \
             "&LMI_PAYMENT_AMOUNT=1.00" \
             "&LMI_PAYMENT_NO=43636-20160126-1af9dcfd" \
             "&LMI_PAYMENT_DESC=%d0%9f%d1%80%d0%b5%d0%b4%d0%be%d0%bf%d0%bb%d0%b0%d1%82%d0%b0+%d0%b7%d0%b0+%d0%b7%d0%b0%d0%ba%d0%b0%d0%b7+%e2%84%9643636+203108.+%d0%9f%d1%80%d0%be%d0%ba%d0%b0%d1%82+%d1%81%d1%82%d1%83%d0%bb%d0%b0+%d0%94%d0%b6%d0%b5%d1%84" \
             "&LMI_SYS_PAYMENT_DATE=2016-01-26T10%3a53%3a35&LMI_SYS_PAYMENT_ID=43184405" \
             "&LMI_PAID_AMOUNT=1.00&LMI_PAID_CURRENCY=RUB&LMI_PAYER_IDENTIFIER=5XXXXXXXXXXX1756" \
             "&LMI_PAYMENT_METHOD=BankCard&LMI_PAYMENT_REF=602617333335" \
             "&payment_type=BankCard&csrfmiddlewaretoken=M6YLwVgTvzBGibXthvnXzBPtkWYMcaYI" \
             "&LOC_PAYER_ID=c2MAAunltGVErkOQt498tU6rFJEEln1D3yRWPxgRpo6o13KmZnzZqLJIUeKEiaolq45WXqSJ98X7%0aXsuab%2fF2SGohtjbi0%2ffhvJmA2JMdFPXyBk6LojKm&order=43636&LMI_HASH=u4SUMtB0dUiCdEwZU%2brunYOxhWc9TGiL8cXmI37IKi8%3d"
        qs = dict(urlparse.parse_qsl(qs))

        fields = ('LMI_MERCHANT_ID',
                  'LMI_PAYMENT_NO',
                  'LMI_SYS_PAYMENT_ID',
                  'LMI_SYS_PAYMENT_DATE',
                  'LMI_PAYMENT_AMOUNT',
                  'LMI_CURRENCY',
                  'LMI_PAID_AMOUNT',
                  'LMI_PAID_CURRENCY',
                  'LMI_PAYMENT_SYSTEM',
                  'LMI_SIM_MODE'
                  )
        result = calculate_hash(
            qs,
            hashed_fields=fields,
            password='U0HXxS8Ec1bCL1/hgEK98sXBd9C9RBrsoqbAGZefqgI=',
            hash_method='sha256'

        )

        self.assertEquals(result, qs['LMI_HASH'])

    def test_hash_test_site(self):
        qs = {'LMI_CURRENCY': 'RUB',
              'LMI_HASH': 'm8bC0NMnyUrcr/XZXe4HaT0OkKjDLqLG2Rqo9GZZ0ys=',
              'LMI_MERCHANT_ID': '2902fb4a-d618-4b6b-aade-793b95e10c59',
              'LMI_PAID_AMOUNT': '6000.00',
              'LMI_PAID_CURRENCY': 'RUB',
              'LMI_PAYER_COUNTRY': 'RU',
              'LMI_PAYER_IDENTIFIER': '712769976071',
              'LMI_PAYER_IP_ADDRESS': '93.187.185.237',
              'LMI_PAYER_PASSPORT_COUNTRY': 'RU',
              'LMI_PAYMENT_AMOUNT': '6000.00',
              'LMI_PAYMENT_DESC': '\xd0\x9f\xd1\x80\xd0\xb5\xd0\xb4\xd0\xbe\xd0\xbf\xd0\xbb\xd0\xb0\xd1\x82\xd0\xb0 \xd0\xb7\xd0\xb0 \xd0\xb7\xd0\xb0\xd0\xba\xd0\xb0\xd0\xb7 \xe2\x84\x9641034 610434. \xd0\x94\xd0\xb5\xd0\xb4 \xd0\x9c\xd0\xbe\xd1\x80\xd0\xbe\xd0\xb7 \xd0\xb8 \xd0\xa1\xd0\xbd\xd0\xb5\xd0\xb3\xd1\x83\xd1\x80\xd0\xbe\xd1\x87\xd0\xba\xd0\xb0',
              'LMI_PAYMENT_METHOD': 'Test',
              'LMI_PAYMENT_NO': '41034-20151217-e8a416ef',
              'LMI_PAYMENT_REF': '999',
              'LMI_PAYMENT_SYSTEM': '3',
              'LMI_SIM_MODE': '0',
              'LMI_SYS_PAYMENT_DATE': '2015-12-17T12:14:10',
              'LMI_SYS_PAYMENT_ID': '40599192',
              'LOC_PAYER_ID': 'c2MAAlZGbRhFxjndQlWNOhxzNcn3lHl3+OqI2w1OoRt0+OhmqBuekmb5vY+KpuQ/V6RXUDbrnKcy\n3Ef8F8W8RTBvv5Sacp+VlRcX34zLDK66nEi/2uU0',
              'order': '41034',
              'payment_type': 'WebMoney'}

        result = calculate_hash(
            qs,
            hashed_fields=settings.PAYMASTER_HASH_FIELDS,
            password='YOUR_MOMMY_SECRET',
            hash_method='sha256'

        )

        self.assertEquals(result, qs['LMI_HASH'])
