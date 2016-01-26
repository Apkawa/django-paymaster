# -*- coding: utf-8 -*-

from django.dispatch import Signal

invoice_init = Signal(providing_args=["data"])
invoice_confirm = Signal(providing_args=["payer", "invoice"])
invoice_paid = Signal(providing_args=["payer", "invoice"])
success_visited = Signal(providing_args=["data", "invoice"])
fail_visited = Signal(providing_args=["data", "invoice"])


refund_created = Signal(providing_args=["data", "refund"])
refund_success = Signal(providing_args=["data", "refund"])
refund_failure = Signal(providing_args=["data", "refund"])
