import random
from sets import Set

def determineSwipeSideConditions(user, group_average, lostPoints, c, reader): 
    atRecommendedStation = False
    goToAnyLocation = False
    is_cargo = False
    if reader.name == user.goto_location:
        atRecommendedStation = True
    if user.goto_location == 'any':
        goToAnyLocation = True
    if user.is_cargo == 'True':
        is_cargo = True
    selectAppropriateRules(user, group_average, lostPoints, c, reader, atRecommendedStation, is_cargo, goToAnyLocation)
    break

def selectAppropriateRules(user, group_average, lostPoints, c, reader, atRecommendedStation, is_cargo, goToAnyLocation):
    rule = ''
    rules = []
    if is_cargo == True:
        rules.append('RULE_7')
        rules.append('RULE_8')
    #check whether player has zeroed out first
    if atRecommendedStation == False:
        #TDOO: flip a coin between rule 2 and 3
#        if flip(0.5) == 'H':
#            rule = 'RULE_2'
#        else:
#            rule = 'RULE_3'
        rules.append('RULE_3')
    elif atRecommendedStation == True or goToAnyLocation == True:
        #80% of the time, select rule 2        
#        if flip(0.8):
        rule = 'RULE_2'
#        else:
#            rule = 'DO_NOTHING'
         
        
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
	
	
	
	
	
	
	
	
	
	
	