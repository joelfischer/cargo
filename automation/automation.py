import random
from sets import Set
from cargoapp.models import Extra, User, Message, Call, Location, Checkin
import time, urllib, urllib2
from threading import Thread
from string import Template

def determineSwipeSideConditions(user, reader):
    atRecommendedStation = False
    goToAnyLocation = False
    if reader.name == user.goto_location:
        atRecommendedStation = True
    if user.goto_location == 'any':
        goToAnyLocation = True
    if user.goto_location == '' or user.goto_location is None or user.goto_location == 'None':
        goToAnyLocation = True
    return atRecommendedStation, goToAnyLocation

def selectAppropriateRules(user, checkin_credit, group_average, lostPoints, atRecommendedStation, goToAnyLocation):
    rules = []
    if user.is_cargo == True:
        rules.append('RULE_8')
    else:
        if lostPoints:
            rules.append('RULE_6')
        else:
            if atRecommendedStation == True or goToAnyLocation == True:
                #80% of the time, select rule 2
        #        if flip(0.8):
                rules.append('RULE_2')
        #        else:
        #            rule = 'DO_NOTHING'
            elif atRecommendedStation == False:
                #flip a coin between rule 2 and 3
        #        if flip(0.5) == 'H':
        #            rule = 'RULE_2'
        #        else:
        #            rule = 'RULE_3'
                rules.append('RULE_3')

    #determine whether a threshold has been exceeded
    extras = Extra.objects.all()
    for extra in extras:
        if extra.name == 'PLAYER_THRESHOLD':
            try:
                threshold = int(extra.value)
            except Exception as e:
                print e
            if user.credit >= threshold:
                #check whether this is a new excess
                if user.credit-checkin_credit < threshold:
                    if user.is_fake == False and user.is_cargo == False:
                        rules.append('RULE_5')
        if extra.name == 'GROUP_THRESHOLD':
            try:
                threshold = int(extra.value)
            except Exception as e:
                print e
            if group_average >= threshold:
                #check whether this is a new excess, need group size
                users = User.objects.all()
                counter = 0
                for usr in users:
                    if usr.group == user.group:
                        counter += 1
                if group_average-checkin_credit/counter < threshold:
                    rules.append('RULE_10')
    return rules


def flip(p):
    return True if random.random() < p else False

def pickRecipient(group_id, not_user):
    users = User.objects.filter(group=group_id).order_by('?')
    for user in users:
        if not user.is_cargo and not user == not_user:
            return user

def getGroups():
    users = User.objects.all()
    groups = Set()
    for user in users:
        groups.add(user.group)
    return groups

def contactPlayer(name, number, message_name, message_content, params, is_SMS):
    if is_SMS:
        sendSMS(name,number,message_name,message_content,params)
    else:
        makeCall(name,number,message_name,message_content,params)
    
    
def makeCall(name, number, message_name, message_content, params):
    token = '13acde1200cc5142acde42576458b5b7a48c638058a26304bdf34c476b11647b18c0da3b5ce13ceb7cb852a5';
    msg = Template(message_content).safe_substitute(params)

    print '##### CALLING #####'
    print name
    print msg

    call = createCall(name, message_name, msg, False)

    try:
        data = urllib.urlencode({"action":"create", "token":token, 'numberToCall':number, 'messageToSay':msg, 'call_id':str(call.id)})
        url = 'http://api.tropo.com/1.0/sessions?' + data
        page = urllib.urlopen(url)
        response = page.read()
    except Exception as e:
        print e;
        call.status = -3;
        call.save();

def makeCallWithDelay(name, number, message_name, message_content, params,delay):
    time.sleep(delay)
    makeCall(name, number, message_name, message_content, params)

def getCargoInGroup(groupNo):
    users = User.objects.filter(group=groupNo)
    return users.get(is_cargo=True)

def sendSMS(name, number, message_name, message_content, params):
    print "******Sending SMS*********"
    print name
    
    msg = Template(message_content).safe_substitute(params)
    print msg
    
    call = createCall(name, message_name, msg, True)
    
    url="https://secure.itagg.com/smsg/sms.mes"
    data = urllib.urlencode({"usr":"CL-SimonEvans", "pwd":"ucTv}6tb7", "from":"+441138685351", "to":str(number), "type":"text","route":"7", "txt":msg})
#    proxy = urllib2.ProxyHandler({'http': '128.243.20.248:3128'})
#    opener = urllib2.build_opener(proxy)
#    urllib2.install_opener(opener)
    page = urllib2.urlopen(url,data)
    print page.read()
    
def createCall(recipient_name, message_title, message_content, is_SMS):
    call = Call(callee=recipient_name, message=message_title, content = message_content, is_SMS = is_SMS)
    call.save();
    return call

def sendMessageToCop(user):
    number = user.phone_num
    name = user.name
    
    msg = "Player has zeroed out: Name " + name + ". Phone number: +" + number
    copNumber = Extra.objects.filter(name="COP_NUMBER").order_by('?')[0]
    
    sendSMS("COP",copNumber.value, "Zeroed player", msg, {})


def processRules(rules, user, param):
    for rule in rules:
        if rule == 'RULE_5':
            #callee = pickRecipient(user.group, user)
            callee = getCargoInGroup(user.group)
            # Make a call with delay
            max_threshold = None
            max_threshold_value = 0
            for threshold in Extra.objects.filter(name='PLAYER_THRESHOLD'):
                if user.credit >= int(threshold.value) and int(threshold.value) >= max_threshold_value:
                    max_threshold = threshold
                    max_threshold_value = int(threshold.value)
            msg = Message.objects.get(name=max_threshold.for_object_id)
            params = {"points":max_threshold.value, "name":callee.name, "target":user.name}
            # Launch new thread to make a call after 60 seconds.
            t = Thread(target=makeCallWithDelay, args=(callee.name, callee.phone_num, msg.name, msg.content, params, 50))
            t.start()
        if rule == 'RULE_10':
            groups = getGroups()
            for group in groups:
                #callee = pickRecipient(group, None)
                callee = getCargoInGroup(group)
                if group == user.group:
                # Make a call with delay
                    msg = Message.objects.get(name='RULE_10A')
                else:
                    msg = Message.objects.get(name='RULE_10B')
                params = {}
                t = Thread(target=makeCallWithDelay, args=(callee.name, callee.phone_num, msg.name, msg.content, params, 80))
                t.start()
        if rule == 'RULE_2':
            user.goto_location = None
            user.save()
            try:
                probability = int(Extra.objects.get(name='CALL_PROBABILITY').value)
            except Exception as e:
                print e

            if flip(probability/100.0):
                # Make a call
                callee = user
                location = pickHighValueLocation(callee)
                if location is not None:
                    user.goto_location = location.name
                    user.save()
                    params = {'name':user.name,'location':location.name}
                    msg = Message.objects.get(name='RULE_2')
                    makeCall(callee.name, callee.phone_num, msg.name, msg.content, params)
        else:
            if rule == 'RULE_8':
                # Make a call
                #callee = pickRecipient(user.group, None)
                #msg = Message.objects.get(name='RULE_7')
                #makeCall(callee, msg, {})
                callee = user
                msg = Message.objects.get(name='RULE_8')
                makeCall(callee, msg, {})
            elif rule == 'RULE_6':
                callee = getCargoInGroup(user.group)
                msg = Message.objects.get(name='RULE_6')
                params = {'target':user.name, 'name':callee.name}
                makeCall(callee.name, callee.phone_num, msg.name, msg.content, params)
                sendMessageToCop(user)
            elif rule == 'RULE_3':
                callee = user
                params = {'location':user.goto_location, 'name' : user.name}
                msg = Message.objects.get(name='RULE_3')
                makeCall(callee.name, callee.phone_num, msg.name, msg.content, params)
                user.goto_location = None
                user.save()


def pickHighValueLocation(user):
    locations = Location.objects.filter(credit__gte=int(Extra.objects.get(name='HIGH_VALUE_LOCATION').value)).order_by('?')
    visited_locations = Checkin.objects.filter(rfid=user.rfid)
    for loc in locations:
        if visited_locations.filter(name=loc.name):
            pass
        else:
            return loc
    return None

def contactAllPlayers(msg, is_SMS):
    users = User.objects.all()
    for callee in users:
        params = {"name":callee.name, "points":callee.credit}
        if (is_SMS):
            sendSMS(callee.name, callee.phone_num, msg.name, msg.content, params)
        else:
            makeCall(callee.name, callee.phone_num, msg.name, msg.content, params)
        
def contactCargoPlayers(msg, is_SMS):
    users = User.objects.filter(is_cargo=True)
    for callee in users:
        params = {"name":callee.name, "points":callee.credit}
        if (is_SMS):
            sendSMS(callee.name, callee.phone_num, msg.name, msg.content, params)
        else:
            makeCall(callee.name, callee.phone_num, msg.name, msg.content, params)
