# coding: utf-8
from __future__ import unicode_literals

import logging
import time

import datetime
from django.core.management import BaseCommand
from django.db.transaction import atomic

from paymaster.models import Refund, Invoice

from paymaster.rest_api.client import PaymasterApiClient
from paymaster.signals import refund_created, refund_failure, refund_success, invoice_paid

logger = logging.getLogger(__name__)

API_MAP = {
    'SiteInvoiceID': 'number',
    'Purpose': 'description',
    'Amount': 'amount',
    'CurrencyCode': 'currency',
    'PaymentAmount': 'paid_amount',
    'PaymentCurrencyCode': 'paid_currency',
    'PaymentSystemID': 'payment_system',
    'PaymentMethod': 'payment_method',
    'PaymentID': 'payment_id',
    'LastUpdateTime': 'payment_date',
    'UserIdentifier': 'payer_id',
}

class Command(BaseCommand):
    help = "Синхронизация оплат и возвратов"

    args = []
    requires_system_checks = True

    def add_arguments(self, parser):
        parser.add_argument(
                '--loop',
                action='store_true',
                dest='loop',
        )

    @atomic
    def update_payment(self, payment_data):
        logging.debug("update_payment: %s", payment_data)

        update_data = {
            'status': payment_data['State'],
        }

        try:
            invoice = Invoice.objects.get(number=payment_data['SiteInvoiceID'])
        except Invoice.DoesNotExist:
            logging.info("Not found invoice: %(SiteInvoiceID)s", **payment_data)
            return None

        if invoice.is_finish():
            # Закрытые счета не обновляем
            logging.info("Invoice %s already closed", invoice.number)
            return None

        if update_data['status'] == Invoice.STATUS_COMPLETE:
            # Если комплит - то мы проставляем оплату
            for f_key, t_key in API_MAP.items():
                update_data[t_key] = payment_data[f_key]

        for key, value in update_data.items():
            setattr(invoice, key, value)

        invoice.save()
        if invoice.is_complete():
            invoice_paid.send(sender=self, payer=None, invoice=invoice)
            logging.info("SUCCESS: Invoice %s", invoice.number)


    @atomic
    def update_refund(self, refund_data):
        logging.debug("update_refund: %s", refund_data)
        update_data = {
            'status': refund_data['State'],
            'refund_date': refund_data['LastUpdate'],
            'error_code': refund_data['ErrorCode'] or None,
            'error_description': refund_data['ErrorDesc'] or None,
        }
        defaults = {
            'payment_id': refund_data['PaymentID'],
            'amount': refund_data['Amount'],
        }
        defaults.update(update_data)
        try:
            defaults['invoice'] = Invoice.objects.get(payment_id=defaults['payment_id'])
        except Invoice.DoesNotExist:
            # Инвойса нет в нашей системе, отложим до лучших времен
            logging.debug("SKIP: %s", refund_data['RefundID'])
            return None

        ext_id = refund_data['ExternalID']
        if ext_id:
            # Если ExternalID существует, то возврат был заведен
            refund_obj = Refund.objects.get(id=ext_id, refund_id=refund_data['RefundID'])
            created = False
        else:
            refund_obj, created = Refund.objects.get_or_create(
                    refund_id=refund_data['RefundID'],
                    defaults=defaults
            )

        if created:
            logging.debug("CREATED: %s", refund_data['RefundID'])
            refund_created.send(
                    sender=self,
                    data=refund_data,
                    refund=refund_obj
            )
        elif refund_obj.is_finish():
            # Возврат уже финиширован, апдейтов не будет
            return

        for key, value in update_data.items():
            setattr(refund_obj, key, value)

        refund_obj.save()

        if refund_obj.is_success():
            logging.debug("SUCCESS: %s", refund_data['RefundID'])
            refund_success.send(
                    sender=self,
                    data=refund_data,
                    refund=refund_obj

            )

        elif refund_obj.is_failure():
            logging.debug("FAILURE: %s", refund_data['RefundID'])
            refund_failure.send(
                    sender=self,
                    data=refund_data,
                    refund=refund_obj
            )

    def sync_open_invoices(self):
        client = PaymasterApiClient()
        open_invoices = Invoice.objects.incompleted()
        for invoice in open_invoices:
            invoice_data = client.get_payment_by_invoice_id(invoice.number)
            # Тупейший баг
            invoice_data['SiteInvoiceID'] = invoice.number

            self.update_payment(invoice_data)


    def sync_refund(self):
        client = PaymasterApiClient()

        for row in client.list_refunds(
                period_from=datetime.datetime.now() - datetime.timedelta(days=3))['Refunds']:
            self.update_refund(row)

    def handle(self, **options):

        # httplib.HTTPConnection.debuglevel = 1
        #
        # logging.basicConfig()  # you need to initialize logging, otherwise you will not see anything from requests
        # logging.getLogger().setLevel(logging.DEBUG)
        # requests_log = logging.getLogger("requests")
        # requests_log.setLevel(logging.DEBUG)
        # requests_log.propagate = True

        self.sync_open_invoices()
        self.sync_refund()

        while options.get('loop'):
            # Run as loop
            self.sync_refund()
            time.sleep(10)
