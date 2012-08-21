import random
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