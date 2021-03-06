from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^cargo/checkin/$', 'cargoapp.views.checkin'),
    url(r'^cargo/calls/$', 'cargoapp.views.calls'),
    url(r'^cargo/registration/$', 'cargoapp.views.registration'),
    url(r'^cargo/index/$', 'cargoapp.views.index'),
    url(r'^cargo/setup/$', 'cargoapp.views.setup'),
    url(r'^cargo/$', 'cargoapp.views.index'),
    url(r'^cargo/report_call_status/$', 'cargoapp.views.report_call_status'),
    url(r'^cargo/register_user_post/$','cargoapp.views.register_user_post'),
    url(r'^cargo/players/$','cargoapp.views.view_players'),
    url(r'^cargo/locations/$','cargoapp.views.view_locations'),
    url(r'^cargo/heartbeat/$','cargoapp.views.process_heartbeat'),
    url(r'^cargo/gui/$','cargoapp.views.get_all_status'),
    url(r'^cargo/logout/$','cargoapp.views.logout_view'),
    url(r'^cargo/game/$','cargoapp.views.set_up_game'),
    # url(r'^cargoapp/', include('firesim.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
     url(r'^cargo/admin/', include(admin.site.urls)),
)
