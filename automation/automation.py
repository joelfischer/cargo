import random
from sets import Set
from cargoapp.models import Extra, User

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
		elif rule == 'RULE_10':
			groups = getGroups()
			for group in groups:
				callee = pickRecipient(group, None)
				# Make a call with delay
		elif rule == 'RULE_2':
			probability = Extra.objects.get(name='CALL_PROBABILITY')
			if flip(probability):
				# Make a call
			elif:
				# Don't make a call
		else:
			if rule == 'RULE_7':
				# Make a call
			elif rule == 'RULE_6':
				# Make a call
			elif rule == 'RULE_3':
				# Make a call
			
def getGroups():
	users = User.objects.all()
	groups = Set()
	for user in users:
		groups.add(user.group)
	return groups
	
def pickRecipient(group_id, not_user):
	users = User.objects.get(group=group_id)
	while True:
		user = users.get(int(random()*len(users)))
		if not user.isCargo and not user == not_user:
			return user			
		
def makeCall(user, message, params):
	
	
	
	
	
	
	
	
	
	
	
