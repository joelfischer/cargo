from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext
from django.http import HttpRequest as request_post
import urllib2, urllib, json, httplib, copy, random
from datetime import *
from django import forms
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from cargoapp.models import User, Checkin, Tag, Message, Call, Location, Extra, Game, All_User, All_Checkin
from django.db.models import Max
from django.core import serializers
from string import Template
from automation.automation import determineSwipeSideConditions, selectAppropriateRules, processRules, sendSMS, contactAllPlayers, contactCargoPlayers, contactPlayer
from django.contrib.auth import logout

def index(request):
    values = {}
    return render_to_response('cargoapp/index.html', values, context_instance=RequestContext(request))

@csrf_exempt 
def calls(request):
    values = {}
    users = User.objects.all()
    messages = Message.objects.exclude(name__contains = "RULE")
    
    values = {'users':users, 'messages':messages}

    if (request.method == "POST"):
    	user_id = request.POST.get("user")
    	message_id = request.POST.get("message")
        method = request.POST.get("method")
        
        print ("User initiated call to User " + user_id + " with Message " + message_id + " and method is " + method)
        
        if message_id=='0':
            msg = Message(name = "Custom Message", content = request.POST.get("custom_message"))
        else:
            msg = Message.objects.get(id=message_id)
        
        if user_id == '-1':
            contactAllPlayers(msg, method =="SMS")
            return render_to_response('cargoapp/calls.html', values, context_instance=RequestContext(request));
        if user_id == '-2':
            contactCargoPlayers(msg, method == "SMS")
            return render_to_response('cargoapp/calls.html', values, context_instance=RequestContext(request));
        
    	user = User.objects.get(id=user_id);
        params = {'name':user.name, 'group':user.group, 'points':user.credit, 'alias':user.alias}
    	contactPlayer(user.name, user.phone_num, msg.name, msg.content, params, method == "SMS")
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
def get_score(request):
    number = request.POST.get('number')
    
    try:
        user = User.objects.get(phone_num=number)
    except Exception as e:
        return HttpResponse("Sorry, I do not know who you are. Good bye!")
    
    return HttpResponse("Hello " + user.name + ". You currently have " + str(user.credit) +" credits.")

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
    error_msg = ''
    try:
        #Get posted values
        post_dic = request.POST
        user = str(post_dic.get('user_name'))
        if user is '':
            error_msg = '- Missing user name -'
        number = str(post_dic.get('number'))
        if number is '':
            error_msg += '- Missing phone number -'
        alias = str(post_dic.get('alias'))
        if alias is '':
            error_msg += '- Missing alias -'
        group = str(post_dic.get('group'))
        if group == 'none':
            error_msg += '- Missing group -'
        if str(post_dic.get('is_cargo'))=='True':
            is_cargo = True
        else:
            is_cargo = False
        if str(post_dic.get('is_fake'))=='True':
            is_fake = True
        else:
            is_fake = False 
        game = str(post_dic.get('game'))
        if game == 'none':
            error_msg += '- Missing game -'
        if user != 'None' and user is not '' and number is not '' and alias is not '' and group != 'none' and game != 'none':
            #check whether alias exists
            try:
                t = Tag.objects.get(alias=alias)
                rfid = t.rfid
            except Exception as e:
                print e
                error_msg = str(e) + ' - wrong alias' 
            #check whether we've already associated that tag to a user
            try: 
                u = All_User.objects.get(alias = alias)
                error_msg += '-- Tag with alias "' +alias + '" already assigned to another player --'  
            except Exception as e:
                print e
                #ok, create a new user
                try:
                    initial_credits = int(Extra.objects.get(name="INITIAL_PLAYER_CREDITS").value)
                except Exception as e2:
                    print e2
                    print "WARNING: NO INITIAL_PLAYER_CREDITS found in EXTRAS table"
                    initial_credits = 0

                u = All_User (name = user, phone_num = number, alias = alias, rfid = rfid, credit = int(initial_credits), group = group, is_cargo = is_cargo, is_fake = is_fake, game_name = game)
                u.save()
                m = Message.objects.get(name="RULE_1")
                sendSMS(u.name,"00" + str(u.phone_num), m.name, m.content, {"name":u.name, "group":u.group, "points":u.credit})
                print 'created new player: '+user
    except Exception as e:
        print e 
    all_users = All_User.objects.all()
    all_tags = Tag.objects.all()
    games = Game.objects.all()
    unused_tags = []
    for tag in all_tags:
        exclude_tag = False
        for user in all_users:
            if tag.alias == user.alias:
                exclude_tag = True
        if exclude_tag == False:
            unused_tags.append(tag)   
    values = {'username': user, 'alias': alias, 'number': number, 'error_msg': error_msg, 'all_users': all_users, 'tags':unused_tags, 'games':games}
    return render_to_response('cargoapp/registration.html', values, context_instance=RequestContext(request))

@csrf_exempt 
def checkin(request):
    error_msg=''
    tagId = ''
    all_checkins = {}
    if request.is_ajax():
        update = []
        #return non-displayed checkins.
        try: 
            lastCall = request.session['last_update']
            
            all_checkins = Checkin.objects.all()
            all_users = User.objects.all()
            for checkin in all_checkins:
                checkin_timestamp = int(checkin.checkin_date.strftime('%s%f'))
                lastCall_timestamp = int(lastCall.strftime('%s%f'))
                if (checkin_timestamp-lastCall_timestamp>0):
#                    print str(checkin_timestamp-lastCall_timestamp)
#                    print 'check in SINCE last refresh -- UPDATE -- '
                    update.append(checkin)
                    try: 
                        u = User.objects.get(rfid = checkin.rfid)
                        update.append(u)
                    except Exception as e:
                        print e
                    #convert to json
            update = serializers.serialize("json", update)
        except Exception as e:
            print e
        request.session['last_update'] = datetime.now()
        return HttpResponse(update)
    else: 
        try:
            dic = request.POST
            try:
                tagId = str(dic['tagId'])
                readerId = str(dic['readerId'])
                name = str(dic['name'])
                credit = int(dic['credit'])
                reader_credit = int(dic['credit_total'])
                if str(dic['is_addition'])=='True':
                    is_addition = True
                else:
                    is_addition = False
                print is_addition
            except Exception as e:
                print e
            if tagId is not '':  
                user, user_credit, error, lostPoints = addOrSubtract(tagId, credit, is_addition)
                group_average, error_msg = getGroupAverage(user)
                if error is not '':
                    print 'Check in with unassigned tag -- have you loaded players for this game? ERROR: '+error
                else:
                    print 'User "'+ user.name +'" checked in, new credit: '+ str(user_credit)
                    
                #get current game id
                current_game = 'UNDEFINED'
                try: 
                    current_game = Extra.objects.get(name='CURRENT_GAME').uneditable_value
                except Exception as e:
                    'ERROR: Extra with name CURRENT_GAME cannot be found: '+str(e)
                               
                c = Checkin (location = readerId, rfid = tagId, name=name, reader_credit = reader_credit, user_credit = user_credit, group_average = group_average, game_name = current_game)
                c.save()   
                
                try:
                    reader = Location.objects.get(reader_id=readerId)
                    reader.credit = reader_credit
                    reader.save()
                except Exception as e:
                    error_msg += str(e)
                    print error_msg
                
                if reader is not None:
                    atRecommendedStation, goToAnyLocation = determineSwipeSideConditions(user, reader)
                    rules = selectAppropriateRules(user, credit, group_average, lostPoints, atRecommendedStation, goToAnyLocation)
                    print rules
                    processRules(rules, user, '')
                
                all_checkins = Checkin.objects.order_by('checkin_date')
                all_checkins.reverse()
                all_users = User.objects.all()    
                                    
                print("|-----------------------|")
                print("|----SWIPE processed----|")
                print("|-READER  -|-   TAGID  -|")
                print("|- %s -|-%s-|" % (readerId, tagId) )
                print("|-----------------------|")
                
            else:
                all_checkins = Checkin.objects.order_by('checkin_date')
                all_checkins = all_checkins.reverse()
                all_users = User.objects.all()
                try:
                    current_game = Extra.objects.get(name='CURRENT_GAME')
                except Exception as e:
                    print e
                    current_game = ''
        except Exception as e:                       
            error_msg += str(e)
            print error_msg
        return render_to_response('cargoapp/checkin.html', {'all_checkins': all_checkins, 'all_users': all_users, 'game':current_game},
                                   context_instance=RequestContext(request))

def addOrSubtract(tagId, credit, is_addition):
    error_msg = ''
    lostPoints = False
    print credit
    try:
        user = User.objects.get(rfid = tagId)
        if is_addition:
            user.credit += credit
        else:
            user.credit -= credit
        #RESET user credit if credit is 0
        if credit == 0:
            user.credit = 0
            lostPoints = True
        user.save()
        credit = user.credit
    except Exception as e:
        error_msg = e
    return user, credit, error_msg, lostPoints

def getGroupAverage(user):
    group = user.group
    average_credit = 0.0
    error_msg = ''
    try: 
        group_users = User.objects.filter(group = group)
        num_users = 0
        group_credit = 0
        for user in group_users:
            num_users += 1.0
            group_credit += user.credit
        average_credit = group_credit/num_users
    except Exception as e:
        error_msg = e
    return average_credit, error_msg

@csrf_exempt 
def process_heartbeat(request):
    try:
        dic = request.POST
        readerId = str(dic.get('readerId'))
        initialCredit = int(dic.get('initial_credit'))
        credit = int(dic.get('credit'))
        checkin_credit = int(dic.get('checkin_credit'))
        status = str(dic.get('status'))
        name = str(dic.get('name'))
        
        print 'HEARTBEAT from '+name+", "+status
#        print status
#        print initialCredit, credit, checkin_credit
        location = Location.objects.get(reader_id = readerId)
        if location.last_heartbeat == '' or location.last_heartbeat is None or status == 'NOT CONFIGURED':
            #first heartbeat. return config. 
            location.last_heartbeat = datetime.now()
            location.save()
            config = []
            config.append(location)
            update = serializers.serialize("json", config)
            return HttpResponse(update)
        if location.update_next_heartbeat:
            location.last_heartbeat = datetime.now()
            location.update_next_heartbeat = False
            location.save()
            config = []
            config.append(location)
            update = serializers.serialize("json", config)
            return HttpResponse(update)
        else:
            location.last_heartbeat = datetime.now()
            location.credit = credit
            location.status = status
            location.name = name
            location.save()
        locations = Location.objects.all()   
    except Exception as e:
        print e
    return render_to_response('cargoapp/locations.html', {'all_locations': locations},
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
        #return non-displayed checkins.
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
        
def get_all_status(request):
    if request.is_ajax():
        update = []
        try:        
            users = User.objects.all()
            for user in users:
                update.append(user)
            locations = Location.objects.all()
            for location in locations:
                update.append(location)
            cs = Checkin.objects.all()
            for c in cs: 
                update.append(c)
            calls = Call.objects.all()
            for call in calls:
                update.append(call)
            update = serializers.serialize("json", update)
        except Exception as e:
            print e
        return HttpResponse(update)
    else: 
        return render_to_response('cargoapp/gui.html',
                               context_instance=RequestContext(request))
    
        
def view_players(request):
    all_players = User.objects.all()
    try:
        current_game = Extra.objects.get(name='CURRENT_GAME')
    except Exception as e:
        print e
        current_game = ''
    recent_checkins = []
    for player in all_players:
        try:
            most_recent_checkin = Checkin.objects.filter(rfid=player.rfid).order_by('-checkin_date')[0]
            recent_checkins.append(most_recent_checkin)
        except Exception as e:
            print e
    return render_to_response('cargoapp/players.html', {'all_players': all_players, 'recent_checkins': recent_checkins, 'game':current_game},
                                   context_instance=RequestContext(request))
    
def view_locations(request):
    all_locations = Location.objects.all()
    return render_to_response('cargoapp/locations.html', {'all_locations': all_locations},
                                   context_instance=RequestContext(request))

def logout_view(request):
    logout(request)
    return render_to_response("cargoapp/logout.html", context_instance=RequestContext(request))

def set_up_game(request):
    current_game = ''
    error_msg = ''
    set_game = ''
    #try to find current game
    try:
        C_G = Extra.objects.get(name='CURRENT_GAME')
        if C_G.uneditable_value == '':
            current_game = 'UNDEFINED'
        else:
            current_game = C_G.uneditable_value
    except Exception as e:
        print e
    try:
        dic = request.POST
        if str(dic.get('game')) != 'None':
            set_game = str(dic.get('game'))
        if set_game != '':
            try:
                C_G = Extra.objects.get(name='CURRENT_GAME')
                C_G.value = 'use set up game view to change this'
                C_G.uneditable_value = set_game
                C_G.save()
                current_game = set_game
                loadPlayersAndClearCheckins(current_game)
            except Exception as e:
                error_msg = 'ERROR trying to find Extra with name CURRENT_GAME: '+str(e)
                print error_msg 
    except Exception as e:
        error_msg = 'ERROR setting up game: '+str(e)
        print error_msg
    games = Game.objects.all()
    return render_to_response("cargoapp/game.html", {'games':games, 'error_msg':error_msg, 'current_game':current_game}, context_instance=RequestContext(request))

def loadPlayersAndClearCheckins(current_game):
    User.objects.all().delete()
    checkins = Checkin.objects.all()
    for c in checkins:
        tosave_checkin = All_Checkin (location = c.location, rfid = c.rfid, name=c.name, reader_credit = c.reader_credit, user_credit = c.user_credit, group_average = c.group_average, game_name = c.game_name)
        tosave_checkin.save()
    Checkin.objects.all().delete()
    all_players = All_User.objects.all()
    for player in all_players:
        if player.game_name == current_game:
            u = User (name = player.name, phone_num = player.phone_num, alias = player.alias, rfid = player.rfid, credit = player.credit, group = player.group, is_cargo = player.is_cargo, is_fake = player.is_fake, game_name = player.game_name)
            u.save()

@csrf_exempt            
def receive_PIN(request):
    pin = request.POST.get('PIN');
    number = request.POST.get('sender');
    print('Received PIN: ' + text + '\n From: ' + number);
    matched_msg = None;
    partial_matched_msg = None;
    matched_user = None;
    send_msg = None;
    
    # Check if number sending text is recognised
    try:
        matched_user = User.objects.get(phone_num = number);
    except Exception as e:
        print "Incoming number unknown: " + number;
        
    if matched_user:
        call = Call(callee = matched_user.name + " (" + number + ")", message=text, content = text, is_SMS = False, status = -1)
    else:
        call = Call(callee=number, message=text, content = text, is_SMS = False, status = -1)
    call.save();
    
    for msg in Message.objects.all():
        if msg.name[0]!='#':
            continue;
        pro_msg = process_string(msg.name)
        if pro_msg == pin:
            send_msg = msg;
    
    if send_msg:
        return HttpResponse(send_msg.content);
    else
        return HttpResponse(Template(Message.objects.get(name="#default")).safe_substitute({"pin":pin}));
            
            
@csrf_exempt 
def receive_SMS(request):
    text = request.POST.get('content');
    number = request.POST.get('sender');
    print('Received SMS: ' + text + '\n From: ' + number);
    matched_msg = None;
    partial_matched_msg = None;
    matched_user = None;
    send_msg = None;
    
    # Check if number sending text is recognised
    try:
        matched_user = User.objects.get(phone_num = number);
    except Exception as e:
        print "Incoming number unknown: " + number;
    
    if matched_user:
        call = Call(callee = matched_user.name + " (" + number + ")", message=text, content = text, is_SMS = True, status = -1)
    else:
        call = Call(callee=number, message=text, content = text, is_SMS = True, status = -1)
    call.save();
    
    # Strip text of non alphanumeric characters
    pro_text = process_string(text)
    
    # Check if text matches a message name
    for msg in Message.objects.all():
        if (msg.name[0]=='#')
            continue;
        pro_msg = process_string(msg.name)
        if levenshtein(pro_msg, pro_text) <= len(pro_msg)/5:
            print("Found full match.");
            matched_msg = msg;
        elif pro_text.find(pro_msg) >= 0:
            print("Found partial match.");
            partial_matched_msg = msg;
    
    if matched_msg:
        print("Matched message: " + matched_msg.name);
        send_msg = matched_msg;
    elif partial_matched_msg:
        if partial_matched_msg.name.find('*') < 0:
            send_msg = partial_matched_msg;
            print("Partial match:" + partial_matched_msg.name);
        else:
            print("Partial match not applied:" + partial_matched_msg.name);

    if send_msg:
        pass;
    else:    
        print ("No match: " + text);
        # No match, check if default message exists.
        try:
            send_msg = Message.objects.get(name="default");
        except Exception as e:
            print ("Default message not found.");
    
    # Send message
    if send_msg:
        if send_msg.content:
            if matched_user:
                contactPlayer(matched_user.name + " (" + number+ ")",number, send_msg.name, send_msg.content, {"name":matched_user.name, "text":text, "alias":matched_user.alias}, False);
            else:
                contactPlayer(number,number, send_msg.name, send_msg.content, {"name":"", "text":text, "alias":""}, False);

    return HttpResponse('Done!');

def receive_SMS_get(request):
    text = request.GET.get('message');
    number = request.GET.get('msisdn');
    print('Received SMS: ' + text + '\n From: ' + number);
    matched_msg = None;
    
    call = Call(callee=number, message=text, content = text, is_SMS = True)
    call.save();
    
    pro_text = process_string(text)
    
    for msg in Message.objects.all():
        if levenshtein(process_string(msg.name), process_string(text)) <= len(process_string(msg.name))/5:
            matched_msg = msg;
    
    if matched_msg:
        print("Matched message: " + matched_msg.name)
        contactPlayer(number,number, matched_msg.name, matched_msg.content, {"name":"Bob"}, False);
    else:
        print("No Match: " + text)
    
    return HttpResponse('Done!');
            
def process_string(str):
    processed = '';
    for c in str:
        if c.isalnum():
            processed = processed + c;
    
    return processed.lower()

def printMatrix(m):
    print ' '
    for line in m:
        spTupel = ()
        breite = len(line)
        for column in line:
            spTupel = spTupel + (column, )
        print "%3i"*breite % spTupel

def levenshtein(s1, s2):
    l1 = len(s1)
    l2 = len(s2)

    matrix = [range(l1 + 1)] * (l2 + 1)
    for zz in range(l2 + 1):
      matrix[zz] = range(zz,zz + l1 + 1)
    for zz in range(0,l2):
      for sz in range(0,l1):
        if s1[sz] == s2[zz]:
          matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1, matrix[zz][sz+1] + 1, matrix[zz][sz])
        else:
          matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1, matrix[zz][sz+1] + 1, matrix[zz][sz] + 1)
    return matrix[l2][l1]

        
