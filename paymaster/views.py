# -*- coding: utf-8 -*-

"""
    Обработчики запросов для взаимодействия с API PayMaster
    https://paymaster.ru/Partners/ru/docs/protocol

    @author: Vlasov Dmitry
    @contact: scailer@russia.ru
    @status: stable
"""

import base64
import urllib
import hashlib
import urlparse
from datetime import datetime, timedelta
from uuid import uuid4

from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse, QueryDict
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from paymaster.utils import calculate_hash, format_dt
from .models import Invoice
from . import settings
from . import signals
from . import logger
from . import utils
from . import forms

PayerEncoder = utils.import_class(settings.PAYMASTER_PAYER_ENCODER_CLASS)()


class InitialView(generic.FormView):
    """
        Форма инициации платежа.

        Данный обработчик предназначен для формирования запроса инициации
        платежа. Здесь будут сформированы параметры платежа в соответствии
        с настройками приложения и имеющимися данными пользователя.
    """
    PayerEncoder = PayerEncoder

    _payment_no = None
    user = None

    form_class = forms.DefaultPaymentForm
    template_name = 'paymaster/init.html'

    phone_field = 'phone'
    email_field = 'email'
    amount_key = 'amount'

    success_url = '.'

    def get_user(self, form):
        """
        Пытаемся получить пользователя. Может быть переопределено
        :return:
        """
        if not self.request.user.is_authenticated():
            logger.warn(u'No user. Permission denied.')
            return None
        return self.request.user

    def form_valid(self, form):
        """ Формируем переход на сайт платежной системы """
        self.user = self.get_user(form)
        if not self.user:
            return HttpResponse('NO ACCESS', status=403)

        try:
            url = self.get_payment_url(form)
        except ValidationError:
            return self.form_invalid(form)

        logger.info(
                u'User {0} redirected to {1}'.format(self.user, url)
        )

        return HttpResponseRedirect(url)

    def get_payer(self, form):
        """ Получаем объект-плательщика """
        return self.user

    def get_payer_id(self, form):
        """ Получаем кодированный идентификатор плательщика """
        return PayerEncoder.encode(self.get_payer(form))

    def get_amount(self, form):
        """ Получаем сумму платежа """
        return form.data.get(self.amount_key)

    def get_payment_no(self, form):
        """ Генерируем номер платежа """
        _gen = (settings.PAYMASTER_INVOICE_NUMBER_GENERATOR
                or utils.number_generetor)

        if not self._payment_no:
            number = _gen(self, form)

            while Invoice.objects.filter(number=number).exists():
                number = _gen(self, form)

            self._payment_no = number

        return self._payment_no

    def get_description(self, form):
        """ Получаем описание """
        return _(settings.PAYMASTER_DESCRIPTION_MASK).format(
                payer=self.get_payer(),
                number=self.get_payment_no(form)
        )

    def get_description_base64(self, form):
        """ Пререводим описание в base64 """
        return base64.encodestring(self.get_description(form).encode('utf-8'))

    def get_payer_phone(self, form):
        """ Получаем номер телефона в формате 79031234567 """
        payer = self.get_payer(form)
        phone = getattr(payer, self.phone_field, None)

        if phone is not None:
            return u''.join(x for x in unicode(phone) if x in '1234567890')

    def get_payer_email(self, form):
        """ Получаем электронную почту """
        payer = self.get_payer(form)
        return getattr(payer, self.email_field, None)

    def get_expires(self, form):
        """ Получаем дату истечения счета YYYY-MM-DDThh:mm:ss """
        return (datetime.now() + timedelta(1)).strftime("%Y-%m-%dT%H:%M:%S")

    def get_payment_method(self, form):
        """ Получаем идентификатор платежного метода """
        return settings.PAYMASTER_DEFAULT_PAYMENT_METHOD

    def get_extra_params(self, form):
        """ Дополнительные параметры продавца """
        _d = isinstance(form.data, QueryDict) and form.data.dict() or form.data
        return _d

    def get_payment_url(self, form):
        """
        Формируем ссылку в paymaster
        """
        query_data = self.init_query(form)
        url = self._build_url(settings.PAYMASTER_INIT_URL, query_data=query_data)
        return url

    def get_payment_success_url(self, form):
        """
        Получаем SUCCESS_URL, ссылка может быть динамически составленой

        :param form:
        :return:
        """
        return settings.PAYMASTER_SUCCESS_URL

    def get_payment_failure_url(self, form):
        """
        Получаем FAILURE_URL, ссылка может быть динамически составленой

        :param form:
        :return:
        """
        return settings.PAYMASTER_FAILURE_URL

    def get_invoice_confirmation_url(self, form):
        """
        Получаем INVOICE_CONFIRMATION_URL, ссылка может быть динамически составленой

        :param form:
        :return:
        """
        return settings.PAYMASTER_INVOICE_CONFIRMATION_URL

    def get_payment_notification_url(self, form):
        """
        Получаем PAYMENT_NOTIFICATION_URL, ссылка может быть динамически составленой

        :param form:
        :return:
        """
        return settings.PAYMASTER_PAYMENT_NOTIFICATION_URL

    def get_query_data(self, form):
        data = {
            'LMI_MERCHANT_ID': settings.PAYMASTER_MERCHANT_ID,
            'LMI_SHOP_ID': settings.PAYMASTER_SHOP_ID,
            'LMI_CURRENCY': settings.PAYMASTER_MERCHANT_CURRENCY,
            'LMI_SIM_MODE': settings.PAYMASTER_SIM_MODE,
            'LMI_PAYMENT_AMOUNT': self.get_amount(form),
            'LMI_PAYMENT_NO': self.get_payment_no(form),
            'LMI_PAYMENT_DESC_BASE64': self.get_description_base64(form),
            'LMI_PAYER_PHONE_NUMBER': self.get_payer_phone(form),
            'LMI_PAYER_EMAIL': self.get_payer_email(form),
            'LMI_EXPIRES': self.get_expires(form),
            'LMI_PAYMENT_METHOD': self.get_payment_method(form),
            'LMI_SUCCESS_URL': self.get_payment_success_url(form),
            'LMI_FAILURE_URL': self.get_payment_failure_url(form),
            'LMI_INVOICE_CONFIRMATION_URL': self.get_invoice_confirmation_url(form),
            'LMI_PAYMENT_NOTIFICATION_URL': self.get_payment_notification_url(form),

            'LOC_PAYER_ID': self.get_payer_id(form),
        }

        data.update(self.get_extra_params(form))
        return data

    def init_query(self, form):
        """ Формируем параметры GET запроса """
        data = self.get_query_data(form)

        # Сигнал посылается до создания счета (счет в дельнейшем может быть
        # проигнорирован) с параметрами инициации платежа. Этот сигнал может
        # использоваться для валидации данных (raise ValidationError).
        signals.invoice_init.send(sender=self, data=data)
        data = {k: v for k, v in data.items() if v}
        return data

    def _build_url(self, base_url, query_data):
        query = urllib.urlencode(query_data)
        return '?'.join([unicode(base_url), query])



class ConfirmView(utils.CSRFExempt, generic.View):
    """
        Обработчик предзапроса подтверждения счета (Invoice Confirmation).

        Этот HTTP POST запрос отправляется системой PayMaster на веб-сервер
        продавца, на URL, указанный в настройках, в тот момент, когда
        пользователь выбрал платежную систему и собирается производить платеж.
        Теоритически можно отказаться, однако, как указано в документации,
        запрос пользователю на оплату уходит раньше, и следовательно возможна
        ситуация, когда счет оплачен, но не принят продавцом. Чтобы избежать
        лишних отказов, в данной реализации API отказ невозможен и счет будет
        подтвержден в любом случае.

        При получении этого запроса создается счет в БД продавца и отправлется
        сигнал invoice_confirm c объектом-счетом в качестве параметра.
    """

    def post(self, request):
        # Создание счета в БД продавца
        invoice = Invoice.objects.create_from_api(request.POST)
        logger.info(u'Invoice {0} payment confirm.'.format(invoice.number))
        payer = PayerEncoder.decode(self.request.REQUEST.get('LOC_PAYER_ID'))
        # Отправка сигнал подтверждения счета.
        signals.invoice_confirm.send(sender=self, payer=payer, invoice=invoice)
        return HttpResponse('YES', content_type='text/plain')


class NotificationView(utils.CSRFExempt, generic.View):
    """
        Обработчик уведомления об оплате счета (Payment Notification).

        HTTP POST запрос отправляется продавцу системой PayMaster в том случае,
        когда платеж успешно проведен. Важно понимать, что запрос Payment
        Notification - это единственный запрос, при обработке которого продавцу
        необходимо учитывать принятый платеж (оказывать услугу и т.п.).

        При получении этого запроса счет отмечается в БД как оплаченный и
        отправлется сигнал invoice_paid c объектом-счетом в качестве параметра.
    """

    _hash_fields = settings.PAYMASTER_HASH_FIELDS

    def check_hash(self, data):
        """ Проверка ключа безопасности """
        _hash = calculate_hash(data, hashed_fields=self._hash_fields)
        return _hash == data.get('LMI_HASH')

    def post(self, request):
        if not self.check_hash(request.POST):  # Проверяем ключ
            logger.error(
                    u'Invoice {0} payment failed by reason: HashError'.format(
                            request.POST.get('LMI_PAYMENT_NO')))
            return HttpResponse('HashError')

        try:
            invoice = Invoice.objects.finalize(request.POST)  # Закрываем счет

        except Invoice.InvoiceDuplication:
            logger.error(
                    u'Invoice {0} payment failed by reason: Duplication'.format(
                            request.POST.get('LMI_PAYMENT_NO')))

            return HttpResponse('InvoiceDuplicationError')

        logger.info(u'Invoice {0} paid succesfully.'.format(invoice.number))
        payer = PayerEncoder.decode(self.request.REQUEST.get('LOC_PAYER_ID'))

        # Отправляем сигнал об успешной оплате
        signals.invoice_paid.send(sender=self, payer=payer, invoice=invoice)
        return HttpResponse('', content_type='text/plain')


class SuccessView(utils.CSRFExempt, generic.TemplateView):
    """
        Страница успешного возврата.

        Предназначена исклчительно для уведомления пользователя об
        удачном завершении операции.

        Внимание! Этот запрос НЕ гарантирует оплаты.
    """

    def get(self, request):
        invoice = Invoice.objects.get(number=request.REQUEST['LMI_PAYMENT_NO'])
        logger.info(u'Invoice {0} success page visited'.format(invoice.number))
        signals.success_visited.send(sender=self, invoice=invoice)
        return super(SuccessView, self).get(request)

    def post(self, request):
        return self.get(request)


class FailView(utils.CSRFExempt, generic.TemplateView):
    """
        Страница неуспешного возврата.

        Предназначена исклчительно для уведомления пользователя об
        неудачном завершении операции.
    """

    def get(self, request):
        payment_no = request.REQUEST['LMI_PAYMENT_NO']

        try:
            invoice = Invoice.objects.get(number=payment_no)
            logger.info(
                    u'Invoice {0} fail page visited'.format(invoice.number))

        except Invoice.DoesNotExist:
            invoice = None
            logger.error(
                    u'Invoice {0} DoesNotExist'.format(payment_no))

        signals.fail_visited.send(
                sender=self, data=request.REQUEST, invoice=invoice)

        return super(FailView, self).get(request)

    def post(self, request):
        return self.get(request)


class FakePaymasterView(generic.TemplateView):
    """
    Страница для тестирования оплат без использования paymaster
    """
    template_name = 'paymaster/test.html'

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

    def _build_form(self, url, data, paymaster_keys):
        for key in data.keys():
            if key.startswith('LMI_') and key not in paymaster_keys:
                del data[key]

        form = forms.DictForm(_dict=data)
        form.action_url = self._build_url(url)
        return form

    def build_failure_form(self):
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
        return self._build_form(url, paymaster_data, fields)

    def build_success_form(self):
        url = self._get_configured_url(self.request, 'SUCCESS_URL')
        paymaster_data = self.get_paymaster_data()

        fields = (
            'LMI_MERCHANT_ID',
            'LMI_PAYMENT_NO',
            'LMI_PAYMENT_AMOUNT',
            'LMI_CURRENCY',
        )

        return self._build_form(url, paymaster_data, fields)

    def build_invoice_confirmation_form(self):
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

        return self._build_form(url, paymaster_data, fields)

    def build_payment_notification_form(self):
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
        url = self._get_configured_url(self.request, 'PAYMENT_NOTIFICATION_URL')
        paymaster_data = self.get_paymaster_data()
        paymaster_data['LMI_SIM_MODE'] = paymaster_data.get('LMI_SIM_MODE', 0)
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

        return self._build_form(url, paymaster_data, fields)

    def get_paymaster_data(self):
        paymaster_keys = {}
        for key, value in self.request.REQUEST.items():
            # if key.startswith('LMI_') or key.startswith('AP_'):
            paymaster_keys[key] = value
        return paymaster_keys

    def get_context_data(self, **kwargs):
        context = super(FakePaymasterView, self).get_context_data()
        context['paymaster_keys'] = self.get_paymaster_data()
        self.sys_payment_id = str(uuid4())
        self.sys_payment_date = format_dt(datetime.now())
        return context
