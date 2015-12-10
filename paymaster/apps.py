# coding: utf-8
from __future__ import unicode_literals

from django.apps import AppConfig


class PaymasterConfig(AppConfig):
    name = 'paymaster'

    def ready(self):
        from . import settings
        settings.validate()
