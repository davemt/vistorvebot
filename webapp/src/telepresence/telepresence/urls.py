from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('telepresence',
    # CORE
    url(r'^$', 'core.views.index'),
    url(r'^about/', 'core.views.about', name='about-robots'),
    url(r'^accounts/login/$', 'core.views.login_user', name="login"),
    url(r'^logout/$', 'core.views.logout_user', name="logout"),
    # ADMIN
    url(r'^admin/', include(admin.site.urls)),
    # APPS
    url(r'^robotarmy/', include('telepresence.robotarmy.urls')),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
