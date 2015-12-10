from django.conf.urls import patterns, include, url
from django.contrib import admin
from .test_app.views import NoUserInitialView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^payments/', include('paymaster.urls', namespace='paymaster')),
    url(r'^payments/init_nouser/', NoUserInitialView.as_view()),
    url(r'^init/', NoUserInitialView.as_view()),

)
