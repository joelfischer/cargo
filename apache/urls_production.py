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
	url(r'^report_call_status/$', 'cargoapp.views.report_call_status'),
    url(r'^$', 'cargoapp.views.index'),
    url(r'^register_user_post/$','cargoapp.views.register_user_post'),
    url(r'^players/$','cargoapp.views.view_players'),
    url(r'^locations/$','cargoapp.views.view_locations'),
    url(r'^heartbeat/$','cargoapp.views.process_heartbeat'),
    url(r'^gui/$','cargoapp.views.get_all_status'),
    url(r'^logout/$','cargoapp.views.logout_view'),
    url(r'^get_score/$','cargoapp.views.get_score'),
    url(r'^receive_SMS/$','cargoapp.views.receive_SMS'),
    url(r'^receive_PIN/$','cargoapp.views.receive_PIN'),
    url(r'^game/$','cargoapp.views.set_up_game'),
    # url(r'^cargoapp/', include('cargoapp.foo.urls')),


    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
)
