import random
from sets import Set
from cargoapp.models import Extra, User
import time
from threading import Thread

def determineSwipeSideConditions(user, reader): 
    atRecommendedStation = False
    goToAnyLocation = False
    if reader.name == user.goto_location:
        atRecommendedStation = True
    if user.goto_location == 'any':
        goToAnyLocation = True
    if user.goto_location == '':
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
    
def processRules(rules, user, param):
	for rule in rules:
		if rule == 'RULE_5':
			callee = pickRecipient(user.group, user)
			# Make a call with delay
			max_threshold = None
			max_threshold_value = 0
			for threshold in Extra.objects.filter(name='PLAYER_THRESHOLD')
				if user.credit > threshold.value and threshold.value > max_threshold_value
					max_threshold = threshold
					max_threshold_value = threshold.value
				
			msg = Message.objects.get(name=max_threshold.for_object_id)
			
			params = {"points":max_threshold.value, "name":user.name}
			
			# Launch new thread to make a call after 60 seconds.
			t = Thread(target=makeCallWithDelay, args=(callee, msg, params, 45))
    		t.start()
			
		elif rule == 'RULE_10':
			groups = getGroups()
			for group in groups:
				callee = pickRecipient(group, None)
				if group == user.group
				# Make a call with delay
					msg = Message.objects.get('RULE_10A')
				else
					msg = Message.objects.get('Rule_10B')
				params = {}
				t = Thread(target=makeCallWithDelay, args=(callee, msg, params, 90))
    			t.start()
				
		elif rule == 'RULE_2':
			try:
				probability = int(Extra.objects.get(name='CALL_PROBABILITY'))
			except Exception as e:
				print e
			if flip(probability/100.0):
				# Make a call
				callee = user
				location = pickHighValueLocation(user)
				if location == None #If no location found
					continue
				user.goto_location = location.name
				user.save()
				params = {'name':user.name,'location':location.name}
				msg = Message.objects.get(name='RULE_2')
				makeCall(callee, msg, params)
			elif:
				# Don't make a call
				pass
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
				params = {'name':user.name}
				makeCall(callee, msg, params)
				sendMessageToCop(user)
			elif rule == 'RULE_3':
				callee = user
				params = {'location':user.goto_location, 'name' : user.name}
				msg = Message.objects.get(name='RULE_3')
				makeCall(callee, msg, params)
				
			
def getGroups():
	users = User.objects.all()
	groups = Set()
	for user in users:
		groups.add(user.group)
	return groups
	
def pickRecipient(group_id, not_user):
	users = User.objects.filter(group=group_id).order_by('?')
	for user in user:
		if not user.isCargo and not user == not_user:
			return user			
		
def makeCall(user, message, params):
	token = '13acde1200cc5142acde42576458b5b7a48c638058a26304bdf34c476b11647b18c0da3b5ce13ceb7cb852a5';    	
	msg = Template(message.content).safe_substitute(params)
	
	call = Call(callee=user.name, message=msg.name);
	call.save();
	
	try:
        url = 'http://api.tropo.com/1.0/sessions?action=create&token='+ token + '&numberToCall=' + user.phone_num + '&messageToSay=' + msg.content + '&call_id' + str(call.id)
        page = urllib.urlopen(url)
        response = page.read()    
        print response
    except Exception as e:
    	print e;
    	call.status = -3;
    	call.save();
    	
def makeCallWithDelay(user,message,params,delay):
	time.sleep(delay)
	makecCall(user,message,params)
		
def getCargoInGroup(groupNo)
	users = User.objects.filter(group=groupNo)
	return users.get(isCargo=True)

def sendMessageToCop(user)
	number = user.phone_num
	name = user.name
	
	
	
	
