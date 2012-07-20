from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext
from django.http import HttpRequest as request_post
import urllib2, urllib, json
from datetime import *
from django import forms
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from cargoapp.models import User, Checkin
from django.core import serializers

def index(request):
    values = {}
    return render_to_response('cargoapp/index.html', values, context_instance=RequestContext(request))

def calls(request):
    values = {}
    return render_to_response('cargoapp/calls.html', values, context_instance=RequestContext(request))

def registration(request):
    values = {}
    return render_to_response('cargoapp/registration.html', values, context_instance=RequestContext(request))

@csrf_exempt 
def checkin(request):
    error_msg=''
    values = {}
    tagId = ''
    all_checkins = {}
    if request.is_ajax():
        update = []
        #TODO: return non-displayed checkins.
        try: 
            all_checkins = Checkin.objects.all()
            for checkin in all_checkins:
                if checkin.displayed == False:
                    update.append(checkin)
                    checkin.displayed = True
                    checkin.save()
                    #TODO: convert to json
                    update = serializers.serialize("json", update)
        except Exception as e:
            print e
        return HttpResponse(update)
    else: 
        try:
            dic = request.POST
            try:
                tagId = str(dic['tagId'])
                readerId = str(dic['readerId'])
            except Exception as e:
                print e
            if tagId is not '':         
#                try:
#                    r = RFID.objects.create(rfid = tagId)
#                    r.save()
#                except Exception as e:
#                    print e
#                    r = RFID.objects.get(rfid = tagId)
                c = Checkin (location = readerId, rfid = tagId)
                c.save()                       
#                c.rfid.add(r)
         
#                all_rfids = RFID.objects.all()            
#                print all_rfids 
#                
#                values['tagId'] = tagId
#                values['readerId'] = readerId 
                print("|-----------------------|")
                print("|-------NEW POST--------|")
                print("|-READER  -|-   TAGID  -|")
                print("|- %s -|-%s-|" % (readerId, tagId) )
                print("|-----------------------|")
                all_checkins = Checkin.objects.all()
            else:
                #this is a browser request, mark as displayed
                all_checkins = Checkin.objects.all()
                for checkin in all_checkins:
                    checkin.displayed = True
                    checkin.save()
        except Exception as e:                       
            error_msg = str(e)
            print error_msg
        return render_to_response('cargoapp/checkin.html', {'all_checkins': all_checkins},
                                   context_instance=RequestContext(request))
    

# Create your views here.
