from django.conf.urls import include, url
from django.contrib import admin
from .views import NoUserInitialView

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^payments/', include('paymaster.urls', namespace='paymaster')),
    url(r'^payments/init_nouser/', NoUserInitialView.as_view()),
    url(r'^init/', NoUserInitialView.as_view()),
]
