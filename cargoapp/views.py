from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext
from django.http import HttpRequest as request_post
import urllib2, urllib, json, httplib
from datetime import *
from django import forms
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from cargoapp.models import User, Checkin, Tag, Message, Call
from django.core import serializers

def index(request):
    values = {}
    return render_to_response('cargoapp/index.html', values, context_instance=RequestContext(request))

@csrf_exempt 
def calls(request):
    values = {}
    users = User.objects.all()
    messages = Message.objects.all()
    
    values = {'users':users, 'messages':messages}
    
    if (request.method == "POST"):
    	token = '13acde1200cc5142acde42576458b5b7a48c638058a26304bdf34c476b11647b18c0da3b5ce13ceb7cb852a5';
    	user_id = request.POST.get("user");
    	message_id = request.POST.get("message");
    	
    	user = User.objects.get(id=user_id);
    	msg = Message.objects.get(id=message_id);
    	
    	call = Call(callee=user.name, message=msg.name);
    	call.save();
    	
    	try:
    		#conn = httplib.HTTPConnection('api.tropo.com');
    		conn = httplib.HTTPConnection('128.243.20.248',3128);
    		conn.request("GET", 'http://api.tropo.com/1.0/sessions?action=create&token='+token+'&numberToCall='+user.phone_num+'&messageToSay='+msg.content+'&call_id='+str(call.id));
    	    
    		if (conn.getresponse()):
    			return render_to_response('cargoapp/calls.html', values, context_instance=RequestContext(request));
    		else:
    			call.status = -3;
    			call.save();
    			return render_to_response('cargoapp/calls.html', values, context_instance=RequestContext(request));
    	except Exception as e:
    		print e;
    		call.status = -3;
    		call.save();
    		return render_to_response('cargoapp/calls.html', values, context_instance=RequestContext(request));
    	
    if request.is_ajax():
        update = []
        #TODO: return non-displayed checkins.
        count = 0;
        try: 
            all_calls = Call.objects.all()
            for call in all_calls:
                    update.append(call);
                    #: convert to json
                    count = count +1;
            update = serializers.serialize("json", update);
        except Exception as e:
            print e
        return HttpResponse(update)
    else:

		return render_to_response('cargoapp/calls.html', values, context_instance=RequestContext(request))

@csrf_exempt 
def report_call_status(request):
	call_id = request.POST.get('call_id');
	call_status = request.POST.get('call_status');
	
	print 'Received call status update:'
	print call_id
	print call_status
	
	call = Call.objects.get(id=call_id);
	call.status = call_status;
	call.save();
	
	return HttpResponse('Done!');

@csrf_exempt 
def register_user_post(request):
	tag_alias = request.POST.get('alias');
	name = request.POST.get('name');
	number = request.POST.get('number');
	print('Modifying user: ' + name + '\n Number: ' + number + '\n Tag alias: ' + tag_alias);
	
	try:
		tag = Tag.objects.get(alias=tag_alias);
	except Exception as e:
		# TODO: Inform user that tag is incorrect.
		print('Warning, incorrect tag received.')
		print e;
		return HttpResponse('Tag not found');
	else:
		user = User.objects.get(rfid=tag.rfid);
		user.phone_num= "+" + number;
		user.name = name;
		user.save();
		return HttpResponse('Done!');
						
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