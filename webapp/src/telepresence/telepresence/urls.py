from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('telepresence',
    # CORE
    (r'^$', 'core.views.index'),
    url(r'^login/$', 'core.views.login_user', name="login"),
    url(r'^logout/$', 'core.views.logout_user', name="logout"),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
