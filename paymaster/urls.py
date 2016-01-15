# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from . import fake_views

from . import views
from . import forms
from . import settings

urlpatterns = patterns('',
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
    url(r'^fail/',
        views.FailView.as_view(template_name='paymaster/fail.html'),
        name='fail'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url('^test/', fake_views.TestPaymasterView.as_view(), name='test'),
        url('^fake/', fake_views.FakePaymasterView.as_view(), name='fake'),
    )