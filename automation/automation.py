import random


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