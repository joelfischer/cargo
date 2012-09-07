from django.db import models

class User(models.Model):
    game_name = models.CharField(max_length=30) #Game.name
    name = models.CharField(max_length=50)
    phone_num = models.CharField(max_length=30)
    group = models.CharField(max_length=30, choices=[('1', '1'), ('2', '2') , ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'),
                                                     ('11', '11'), ('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),
                                                     ('21', '21'),('22', '22'),('23', '23'),('24', '24'),('25', '25')])
    alias = models.CharField(max_length=30)
    rfid = models.CharField(max_length=200, editable=False)
    is_cargo = models.BooleanField() 
    is_fake = models.BooleanField() 
    credit = models.IntegerField(max_length=10)
    goto_location = models.CharField(max_length=30, blank = True, null=True)
    def __unicode__(self):
        return self.name

class All_User(models.Model):
    game_name = models.CharField(max_length=30) #Game.name
    name = models.CharField(max_length=50)
    phone_num = models.CharField(max_length=30)
    group = models.CharField(max_length=30, choices=[('1', '1'), ('2', '2') , ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'),
                                                     ('11', '11'), ('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),
                                                     ('21', '21'),('22', '22'),('23', '23'),('24', '24'),('25', '25')])
    alias = models.CharField(max_length=30)
    rfid = models.CharField(max_length=200, editable=False)
    is_cargo = models.BooleanField() 
    is_fake = models.BooleanField() 
    credit = models.IntegerField(max_length=10)
    goto_location = models.CharField(max_length=30, blank = True, null=True)
    def __unicode__(self):
        return self.name
    
class Location(models.Model):
    reader_id = models.CharField(max_length=30, unique=True) 
    name = models.CharField(max_length=30)
    init_credit = models.IntegerField(max_length=10)
    checkin_credit = models.IntegerField(max_length=10)
    credit = models.IntegerField(max_length=10, editable = False, null = True)
    is_addition = models.BooleanField(default = True)
    status = models.CharField(max_length=30, default = 'unseen', editable = False)
    last_heartbeat = models.DateTimeField(editable=False, blank=True, null=True)
    allow_multiple_checkins = models.BooleanField(default = False)
    reset_local_checkin_history = models.BooleanField(default = True) 
    update_next_heartbeat = models.BooleanField()
    def __unicode__(self):
        return self.name

class Checkin(models.Model):
    game_name = models.CharField(max_length=30) #Game.name
    location = models.CharField(max_length=200) #Location.name
    name = models.CharField(max_length=30)  #Location.reader_id 
    rfid = models.CharField(max_length=200) #User.rfid, #Tag.rfid
    reader_credit = models.IntegerField(max_length=10)
    user_credit = models.IntegerField(max_length=10)
    checkin_date = models.DateTimeField(auto_now_add=True)
    group_average = models.FloatField(max_length=10)
    def __unicode__(self):
        return unicode(self.checkin_date)
    
class All_Checkin(models.Model):
    game_name = models.CharField(max_length=30) #Game.name
    location = models.CharField(max_length=200) #Location.name
    name = models.CharField(max_length=30)  #Location.reader_id 
    rfid = models.CharField(max_length=200) #User.rfid, #Tag.rfid
    reader_credit = models.IntegerField(max_length=10)
    user_credit = models.IntegerField(max_length=10)
    checkin_date = models.DateTimeField(auto_now_add=True)
    group_average = models.FloatField(max_length=10)
    def __unicode__(self):
        return unicode(self.checkin_date)
    
class Tag(models.Model):
    rfid = models.CharField(max_length=200, unique = True, editable=True)
    alias = models.CharField(max_length=200, unique = True)
    assigned = models.BooleanField()    
    def __unicode__(self):
        return self.rfid
    
class Message(models.Model):
	name = models.CharField(max_length=200, unique = True)
	content = models.TextField()
	def __unicode__(self):
		return unicode(self.name)    

class Call(models.Model):
    callee = models.CharField(max_length=200)
    message = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=0)
    is_SMS = models.BooleanField(default=False)
    content = models.TextField()
    def __unicode__(self):
		return unicode(self.id)   
  

class Extra(models.Model):
    for_object_id = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    value = models.CharField(max_length=100)
    uneditable_value = models.CharField(max_length=30, editable=False)
    def __unicode__(self):
        return self.name
    
class Game(models.Model):
    name = models.CharField(max_length=30, unique = True)
    def __unicode__(self):
        return self.name
    
