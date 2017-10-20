# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import fake_views

from . import views
from . import forms
from . import settings

urlpatterns = [
    url(r'^init/', views.InitialView.as_view(
        form_class=forms.DefaultPaymentForm,
        template_name='paymaster/init.html',
        amount_key='amount'),
        name='init'),

    url(r'^confirm/', views.ConfirmView.as_view(), name='confirm'),
    url(r'^paid/', views.NotificationView.as_view(), name='paid'),
    url(r'^success/',
        views.SuccessView.as_view(template_name='paymaster/success.html'),
        name='success'),
    url(r'^failure/',
        views.FailView.as_view(template_name='paymaster/fail.html'),
        name='failure'),
    # DEPRECATED
    url(r'^fail/',
        views.FailView.as_view(template_name='paymaster/fail.html'),
        name='fail'),
]

urlpatterns += [
    url('^test/', fake_views.TestPaymasterView.as_view(), name='test'),
    url('^fake/', fake_views.FakePaymasterView.as_view(), name='fake'),
]
