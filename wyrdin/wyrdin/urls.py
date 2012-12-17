from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wyrdin.views.home', name='home'),
    # url(r'^wyrdin/', include('wyrdin.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # url(r'^transcribe$',
    #     'wyrdin.views.func_name',
    #     name='transcribe'),

    url(r'^admin/', include(admin.site.urls)),
)
