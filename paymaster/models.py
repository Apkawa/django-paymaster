# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from .managers import InvoiceManager, InvoiceDuplication

from .rest_api.client import ERROR_CODE_MAP


class Invoice(models.Model):
    number = models.CharField(
            _(u'Номер счета'), max_length=128, unique=True)
    description = models.CharField(
            _(u'Назначение платежа'), max_length=256)
    amount = models.DecimalField(
            _(u'Сумма платежа, заказанная продавцом'),
            max_digits=11, decimal_places=2)
    currency = models.CharField(
            _(u'Валюта платежа, заказанная продавцом'), max_length=3)
    paid_amount = models.DecimalField(
            _(u'Сумма платежа в валюте, в которой покупатель производит платеж'),
            max_digits=11, decimal_places=2)
    paid_currency = models.CharField(
            _(u'Валюта, в которой производится платеж'), max_length=3)
    payment_method = models.CharField(
            _(u'Идентификатор платежной системы, выбранной покупателем'),
            max_length=50)
    payment_system = models.CharField(
            _(u'Идентификатор платежного метода'), max_length=50)

    payment_id = models.CharField(
            _(u'Номер платежа в системе PayMaster'),
            max_length=50, null=True, blank=True)
    payer_id = models.CharField(
            _(u'Идентификатор плательщика в платежной системе'),
            max_length=50, null=True, blank=True)
    payment_date = models.DateTimeField(
            _(u'Дата платежа'), null=True, blank=True)

    creation_date = models.DateTimeField(
            _(u'Дата создания записи'), auto_now_add=True)
    edition_date = models.DateTimeField(
            _(u'Дата последнего изменения'), auto_now=True)

    objects = InvoiceManager()

    InvoiceDuplication = InvoiceDuplication

    def is_paid(self):
        return bool(self.payment_date)

    def __unicode__(self):
        if self.is_paid():
            return u'{0} {1}'.format(
                    self.number, self.payment_date.strftime('%Y-%m-%d'))

        return u'{0} (no paid)'.format(self.number, self.payment_date)

    class Meta:
        verbose_name = _(u'Счет')
        verbose_name_plural = _(u'Счета')


class Refund(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='refunds')

    payment_id = models.CharField(u"ID платежа в системе Paymaster", max_length=50)
    refund_id = models.CharField(u'ID возврата в системе Paymaster', max_length=64, unique=True)

    STATUS_NEW = 'NEW'
    STATUS_PENDING = "PENDING"
    STATUS_EXECUTING = "EXECUTING"
    STATUS_SUCCESS = "SUCCESS"
    STATUS_FAILURE = "FAILURE"

    STATUS_CHOICES = (
        (STATUS_NEW, u'Создан'),
        (STATUS_PENDING, u'Поставлен в очередь на совершение операции возврата'),
        (STATUS_EXECUTING, u'Проведение транзакции возврата платежа'),
        (STATUS_SUCCESS, u'Возврат средств успешно завершен'),
        (STATUS_FAILURE, u'возврат средств не осуществлен')

    )
    status = models.CharField(u"Статус возврата", max_length=20,
            choices=STATUS_CHOICES, default=STATUS_NEW)

    amount = models.DecimalField(
            _(u'Сумма возврата'),
            max_digits=11, decimal_places=2)

    ERROR_CODE_CHOICES = ERROR_CODE_MAP.items()
    error_code = models.SmallIntegerField(u"Код ошибки", choices=ERROR_CODE_CHOICES, null=True, blank=True)
    error_description = models.TextField(u"Описание ошибки", null=True, blank=True)

    refund_date = models.DateTimeField(_(u"Дата обновления возврата"))

    creation_date = models.DateTimeField(
            _(u'Дата создания записи'), auto_now_add=True)
    edition_date = models.DateTimeField(
            _(u'Дата последнего изменения'), auto_now=True)

    class Meta:
        verbose_name = _(u'Возврат')
        verbose_name_plural = _(u'Возвраты')

    def is_finish(self):
        return self.is_failure() or self.is_success()

    def is_process(self):
        return not self.is_finish()

    def is_failure(self):
        return self.status == self.STATUS_FAILURE

    def is_success(self):
        return self.status == self.STATUS_SUCCESS
