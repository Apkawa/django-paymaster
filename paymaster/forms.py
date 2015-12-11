# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _


class DefaultPaymentForm(forms.Form):
    amount = forms.DecimalField(
        label=_(u'Сумма'), min_value=10,
        max_value=9999999, required=True)


class DictForm(forms.Form):
    def __init__(self, _dict, *args, **kwargs):
        for key, value in _dict.items():
            self.base_fields[key] = forms.CharField(widget=forms.HiddenInput, initial=value)
        super(DictForm, self).__init__(*args, **kwargs)
