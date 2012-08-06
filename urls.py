from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^checkin/$', 'cargoapp.views.checkin'),
    url(r'^calls/$', 'cargoapp.views.calls'),
    url(r'^registration/$', 'cargoapp.views.registration'),
    url(r'^index/$', 'cargoapp.views.index'),
    url(r'^setup/$', 'cargoapp.views.setup'),
    url(r'^handle_registration/$', 'cargoapp.views.handle_reg'),
    url(r'^report_call_status/$', 'cargoapp.views.report_call_status'),
    url(r'^register_user_post/$','cargoapp.views.register_user_post'),
    url(r'^$', 'cargoapp.views.index'),
    # url(r'^cargoapp/', include('firesim.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
)
