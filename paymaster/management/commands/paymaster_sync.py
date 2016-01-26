# coding: utf-8
from __future__ import unicode_literals

import time

import datetime
from django.core.management import BaseCommand
from django.db.transaction import atomic

from paymaster.models import Refund, Invoice

from paymaster.rest_api.client import PaymasterApiClient
from paymaster.signals import refund_created, refund_failure, refund_success


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
        # TODO
        pass

    @atomic
    def update_refund(self, refund_data):
        print refund_data
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
            print "SKIP", refund_data['RefundID']
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
            print "CREATED", refund_data['RefundID']
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
            print "SUCCESS", refund_data['RefundID']
            refund_success.send(
                    sender=self,
                    data=refund_data,
                    refund=refund_obj

            )

        elif refund_obj.is_failure():
            print "FAILURE", refund_data['RefundID']
            refund_failure.send(
                    sender=self,
                    data=refund_data,
                    refund=refund_obj
            )

    def sync_refund(self):
        client = PaymasterApiClient()

        for row in client.list_refunds(
                period_from=datetime.datetime.now() - datetime.timedelta(days=1))['Refunds']:
            self.update_refund(row)

    def handle(self, **options):

        # httplib.HTTPConnection.debuglevel = 1
        #
        # logging.basicConfig()  # you need to initialize logging, otherwise you will not see anything from requests
        # logging.getLogger().setLevel(logging.DEBUG)
        # requests_log = logging.getLogger("requests")
        # requests_log.setLevel(logging.DEBUG)
        # requests_log.propagate = True

        self.sync_refund()

        while options.get('loop'):
            # Run as loop
            self.sync_refund()
            time.sleep(10)
