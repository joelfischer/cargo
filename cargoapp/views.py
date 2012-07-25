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
<<<<<<< HEAD
from cargoapp.models import User, Checkin, Tag
=======
from cargoapp.models import User, Checkin, Message
>>>>>>> Added basic Calls view functionality
from django.core import serializers

def index(request):
    values = {}
    return render_to_response('cargoapp/index.html', values, context_instance=RequestContext(request))

def calls(request):
    values = {}
    users = User.objects.all()
    messages = Message.objects.all()
    
    values = {'users':users, 'messages':messages}
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
    

@csrf_exempt 
def setup(request):
    error_msg=''
    response = ''
    msg = ''
    try:
        dic = request.POST
        alias = str(dic['alias'])
        if (alias is not ''):
            print 'alias found'
            r = Tag.objects.get(alias = '')
            r.alias = alias
            r.save()
    except Exception as e:
        print e
    if request.is_ajax():
        update = []
        #TODO: return non-displayed checkins.
        try: 
            r = Tag.objects.get(alias = '')
            response = r.rfid
        except Exception as e: 
            #we don't have this tag in our db yet, set up.
            print 'no tags found'
            print e
        try: 
            r = Tag.objects.get(assigned = True)
            print 'found old tag'
            alias = r.alias 
            r.assigned = False
            r.save()
            response = 'Already set up this tag with alias: '+alias
        except Exception as e:
            print 'not an old tag'
            print e 
        return HttpResponse(response)
#        try: 
#            all_checkins = Checkin.objects.all()
#            for checkin in all_checkins:
#                if checkin.displayed == False:
#                    update.append(checkin)
#                    checkin.displayed = True
#                    checkin.save()
#                    #TODO: convert to json
#                    update = serializers.serialize("json", update)
#        except Exception as e:
#            print e
#        return HttpResponse(update)
    else: 
        try:
            dic = request.POST
            try:
                tagId = str(dic['tagId'])
                readerId = str(dic['readerId'])
            except Exception as e:
                print e
            if tagId is not '':  
                tag = Tag (rfid = tagId)
                tag.save()        
                print("|-----------------------|")
                print("|-------NEW POST--------|")
                print("|-READER  -|-   TAGID  -|")
                print("|- %s -|-%s-|" % (readerId, tagId) )
                print("|-----------------------|")     
                all_tags = Tag.objects.all()
                print all_tags                           
        except Exception as e:                       
            error_msg = str(e)
            print error_msg
            if error_msg == 'column alias is not unique' or error_msg == 'column rfid is not unique':
                tag = Tag.objects.get(rfid = tagId)
                a_len = tag.alias.__len__()
                print a_len
                #set flag to false to remind user this has already been assigned
                if a_len > 0:
                    tag.assigned = True
                    tag.save()
                    print 'success'
        all_tags = Tag.objects.all()
        return render_to_response('cargoapp/define_tag.html', {'all_tags': all_tags},
                                   context_instance=RequestContext(request))
        
def handle_reg(request):
    response = {'response':'success'}
    return HttpResponse(response)
