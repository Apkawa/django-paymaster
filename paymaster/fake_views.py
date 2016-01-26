# coding: utf-8
from __future__ import unicode_literals

import base64
import urllib
import urlparse
from datetime import datetime
from uuid import uuid4

from django.core.urlresolvers import reverse_lazy
from django.views import generic

from paymaster import settings, forms
from paymaster.utils import calculate_hash, format_dt


class FakePaymasterMixinView(object):
    fallback_urls = {
        'SUCCESS_URL': reverse_lazy('paymaster:success'),
        'FAILURE_URL': reverse_lazy('paymaster:fail'),
        'INVOICE_CONFIRMATION_URL': reverse_lazy('paymaster:confirm'),
        'PAYMENT_NOTIFICATION_URL': reverse_lazy('paymaster:paid'),
    }

    def _get_configured_url(self, request, url_name):
        req_data = request.REQUEST
        return (
            req_data.get('LMI_' + url_name)
            or getattr(settings, 'PAYMASTER_' + url_name)
            or self.fallback_urls[url_name]
        )

    def _build_url(self, base_url, query_kw=None):
        query_kw = query_kw or {}
        url_parts = urlparse.urlparse(base_url)
        query = dict(urlparse.parse_qsl(url_parts.query))
        query.update(query_kw)

        url_parts = list(url_parts)
        url_parts[4] = urllib.urlencode(query)
        return urlparse.urlunparse(url_parts)

    def _clean_paymaster_data(self, data, paymaster_keys=None):
        if not paymaster_keys:
            return data

        for key in data.keys():
            if key.startswith('LMI_') and key not in paymaster_keys:
                del data[key]
        return data

    def _build_form(self, url, data, method='GET', paymaster_keys=None):
        data = self._clean_paymaster_data(data, paymaster_keys)
        form = forms.DictForm(_dict=data)
        form.action_url = self._build_url(url)
        return form

    def get_failure_data(self):
        url = self._get_configured_url(self.request, 'FAILURE_URL')

        paymaster_data = self.get_paymaster_data()
        paymaster_data['LMI_SYS_PAYMENT_ID'] = self.sys_payment_id
        paymaster_data['LMI_SYS_PAYMENT_DATE'] = self.sys_payment_date

        fields = (
            'LMI_MERCHANT_ID',
            'LMI_PAYMENT_NO',
            'LMI_SYS_PAYMENT_ID',
            'LMI_SYS_PAYMENT_DATE',
            'LMI_PAYMENT_AMOUNT',
            'LMI_CURRENCY',
        )
        return {
            'url': url,
            'data': self._clean_paymaster_data(paymaster_data, paymaster_keys=fields),
            'method': 'GET',
        }

    def get_success_data(self):
        paymaster_data = self.get_paymaster_data()

        fields = (
            'LMI_MERCHANT_ID',
            'LMI_PAYMENT_NO',
            'LMI_PAYMENT_AMOUNT',
            'LMI_CURRENCY',
        )

        url = self._get_configured_url(self.request, 'SUCCESS_URL')
        return {
            'url': url,
            'data': self._clean_paymaster_data(paymaster_data, paymaster_keys=fields),
            'method': 'GET',
        }

    def get_invoice_confirmation_data(self):
        url = self._get_configured_url(self.request, 'INVOICE_CONFIRMATION_URL')
        fields = (
            'LMI_PREREQUEST',
            'LMI_MERCHANT_ID',
            'LMI_PAYMENT_NO',
            'LMI_PAYMENT_AMOUNT',
            'LMI_CURRENCY',
            'LMI_PAID_AMOUNT',
            'LMI_PAID_CURRENCY',
            'LMI_PAYMENT_SYSTEM',
            'LMI_PAYMENT_METHOD',
            'LMI_SIM_MODE',
            'LMI_PAYMENT_DESC',
            'LMI_SHOP_ID',
        )
        paymaster_data = self.get_paymaster_data()
        paymaster_data['LMI_PREREQUEST'] = 1
        paymaster_data['LMI_PAID_CURRENCY'] = paymaster_data['LMI_CURRENCY']
        paymaster_data['LMI_PAID_AMOUNT'] = paymaster_data['LMI_PAYMENT_AMOUNT']
        paymaster_data['LMI_PAYMENT_SYSTEM'] = paymaster_data.get('LMI_PAYMENT_SYSTEM', 'WebMoney')

        paymaster_data['LMI_PAYMENT_DESC'] = (
            paymaster_data.get('LMI_PAYMENT_DESC')
            or base64.decodestring(paymaster_data['LMI_PAYMENT_DESC_BASE64'])
        )

        return {
            'url': url,
            'data': self._clean_paymaster_data(paymaster_data, paymaster_keys=fields),
            'method': 'POST',
        }

    def get_payment_notification_data(self):
        url = self._get_configured_url(self.request, 'PAYMENT_NOTIFICATION_URL')
        fields = (
            'LMI_MERCHANT_ID',
            'LMI_PAYMENT_NO',
            'LMI_PAYMENT_AMOUNT',
            'LMI_CURRENCY',
            'LMI_PAYMENT_SYSTEM',
            'LMI_PAYMENT_METHOD',
            'LMI_PAYMENT_DESC',
            'LMI_SHOP_ID',

            'LMI_SIM_MODE',
            'LMI_HASH',
            'LMI_PAYER_IDENTIFIER',
            'LMI_PAYER_COUNTRY',
            'LMI_PAYER_PASSPORT_COUNTRY',
            'LMI_PAYER_IP_ADDRESS',
            'LMI_PAID_AMOUNT',
            'LMI_PAID_CURRENCY',
            'LMI_SYS_PAYMENT_ID',
            'LMI_SYS_PAYMENT_DATE',

        )
        paymaster_data = self.get_paymaster_data()
        paymaster_data['LMI_SIM_MODE'] = paymaster_data.get('LMI_SIM_MODE', None)
        paymaster_data['LMI_PAYMENT_DESC'] = (
            paymaster_data.get('LMI_PAYMENT_DESC')
            or base64.decodestring(paymaster_data['LMI_PAYMENT_DESC_BASE64'])
        )
        paymaster_data['LMI_PAID_CURRENCY'] = paymaster_data['LMI_CURRENCY']
        paymaster_data['LMI_PAID_AMOUNT'] = paymaster_data['LMI_PAYMENT_AMOUNT']
        paymaster_data['LMI_SYS_PAYMENT_ID'] = self.sys_payment_id
        paymaster_data['LMI_SYS_PAYMENT_DATE'] = self.sys_payment_date
        paymaster_data['LMI_PAYER_IDENTIFIER'] = 'test-payer'
        paymaster_data['LMI_PAYMENT_SYSTEM'] = paymaster_data.get('LMI_PAYMENT_SYSTEM', 'WebMoney')

        paymaster_data['LMI_PAYER_COUNTRY'] = paymaster_data['LMI_PAYER_PASSPORT_COUNTRY'] = 'RU'
        paymaster_data['LMI_PAYER_IP_ADDRESS'] = '127.0.0.1'

        paymaster_data['LMI_HASH'] = calculate_hash(paymaster_data, settings.PAYMASTER_HASH_FIELDS)
        return {
            'url': url,
            'data': self._clean_paymaster_data(paymaster_data, paymaster_keys=fields),
            'method': 'POST',
        }

    def build_failure_form(self):
        return self._build_form(**self.get_failure_data())

    def build_success_form(self):
        return self._build_form(**self.get_success_data())

    def build_invoice_confirmation_form(self):
        return self._build_form(**self.get_invoice_confirmation_data())

    def build_payment_notification_form(self):
        return self._build_form(**self.get_payment_notification_data())

    def get_paymaster_data(self):
        paymaster_keys = {}
        for key, value in self.request.REQUEST.items():
            paymaster_keys[key] = value
        return paymaster_keys

    def dispatch(self, request, *args, **kwargs):
        self.sys_payment_id = str(uuid4())
        self.sys_payment_date = format_dt(datetime.now())
        return super(FakePaymasterMixinView, self).dispatch(request, *args, **kwargs)


class TestPaymasterView(FakePaymasterMixinView, generic.TemplateView):
    """
    Страница для тестирования оплат без использования paymaster
    """
    template_name = 'paymaster/fake/test.html'

    def get_context_data(self, **kwargs):
        context = super(TestPaymasterView, self).get_context_data()
        context['paymaster_keys'] = self.get_paymaster_data()
        return context


class FakePaymasterView(FakePaymasterMixinView, generic.TemplateView):
    """
    Страница эмулирующая процесс оплаты в paymaster
    """
    template_name = 'paymaster/fake/fake.html'

    def get_context_data(self, **kwargs):
        context = super(FakePaymasterMixinView, self).get_context_data()
        paymaster_data = self.get_paymaster_data()
        context['paymaster_keys'] = paymaster_data
        context['description'] = base64.decodestring(paymaster_data[u'LMI_PAYMENT_DESC_BASE64'])
        context['number'] = paymaster_data[u'LMI_PAYMENT_NO']
        context['amount'] = paymaster_data[u'LMI_PAYMENT_AMOUNT']
        return context
