import random
from sets import Set
from cargoapp.models import Extra, User, Message, Call, Location
import time, urllib
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
        rules.append('RULE_7')
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

def makeCall(user, message, params):
    token = '13acde1200cc5142acde42576458b5b7a48c638058a26304bdf34c476b11647b18c0da3b5ce13ceb7cb852a5';
    msg = Template(message.content).safe_substitute(params)

    print '##### CALLING #####'
    print user.name
    print msg

    call = Call(callee=user.name, message=message.name);
    call.save();

    try:
        url = 'http://api.tropo.com/1.0/sessions?action=create&token='+ token + '&numberToCall=' + user.phone_num + '&messageToSay=' + msg + '&call_id' + str(call.id)
        page = urllib.urlopen(url)
        response = page.read()
        print response
    except Exception as e:
        print e;
        call.status = -3;
        call.save();

def makeCallWithDelay(user,message,params,delay):
    time.sleep(delay)
    makeCall(user,message,params)

def getCargoInGroup(groupNo):
    users = User.objects.filter(group=groupNo)
    return users.get(is_cargo=True)

def sendMessageToCop(user):
    number = user.phone_num
    name = user.name
    
    msg = "Player has zeroed out: Name " + name + ". Phone number: +" + number
    copNumber = Extra.objects.filter(name="COP_NUMBER").order_by('?')[0]
    
    url="https://secure.itagg.com/smsg/sms.mes"
    data = urllib.urlencode({"usr":"CL-SimonEvans", "pwd":"ucTv}6tb7", "from":"Cargo", "to":copNumber, "type":"text","route":"7", "txt":msg})
#    proxy = urllib2.ProxyHandler({'http': '128.243.20.248:3128'})
#    opener = urllib2.build_opener(proxy)
#    urllib2.install_opener(opener)
    page = urllib2.urlopen(url,data)
    print page.read()


def processRules(rules, user, param):
    for rule in rules:
        if rule == 'RULE_5':
            callee = pickRecipient(user.group, user)
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
            t = Thread(target=makeCallWithDelay, args=(callee, msg, params, 5))
            t.start()
        if rule == 'RULE_10':
            groups = getGroups()
            for group in groups:
                callee = pickRecipient(group, None)
                if group == user.group:
                # Make a call with delay
                    msg = Message.objects.get(name='RULE_10A')
                else:
                    msg = Message.objects.get(name='RULE_10B')
                params = {}
                t = Thread(target=makeCallWithDelay, args=(callee, msg, params, 10))
                t.start()
        if rule == 'RULE_2':
            try:
                probability = int(Extra.objects.get(name='CALL_PROBABILITY').value)
            except Exception as e:
                print e
            if flip(probability/100.0):
                # Make a call
                callee = user
                location = pickHighValueLocation()
                if location is not None:
                    user.goto_location = location.name
                    user.save()
                    params = {'name':user.name,'location':location.name}
                    msg = Message.objects.get(name='RULE_2')
                    makeCall(callee, msg, params)
        else:
            if rule == 'RULE_7':
                # Make a call
                callee = pickRecipient(user.group, None)
                msg = Message.objects.get(name='RULE_7')
                makeCall(callee, msg, {})
                callee = user
                msg = Message.objects.get(name='RULE_8')
                makeCall(callee, msg, {})
            elif rule == 'RULE_6':
                callee = getCargoInGroup(user.group)
                msg = Message.objects.get(name='RULE_6')
                params = {'target':user.name, 'name':callee.name}
                makeCall(callee, msg, params)
                sendMessageToCop(user)
            elif rule == 'RULE_3':
                callee = user
                params = {'location':user.goto_location, 'name' : user.name}
                msg = Message.objects.get(name='RULE_3')
                makeCall(callee, msg, params)
                user.goto_location = None
                user.save()


def pickHighValueLocation():
    locations = Location.objects.filter(credit__gte=int(Extra.objects.get(name='HIGH_VALUE_LOCATION').value)).order_by('?')
    try:
        location = locations[0]
    except Exception as e:
        print e
        return None
    return location
