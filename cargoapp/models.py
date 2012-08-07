from django.db import models

class User(models.Model):
    name = models.CharField(max_length=15)
    phone_num = models.CharField(max_length=30)
    group = models.CharField(max_length=30, choices=[('1', '1'), ('2', '2') , ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')])
    alias = models.CharField(max_length=30)
    rfid = models.CharField(max_length=200, editable=False)
    is_cargo = models.BooleanField() 
    credit = models.IntegerField(max_length=10)
    def __unicode__(self):
        return self.name

class Checkin(models.Model):
    location = models.CharField(max_length=200)
    name = models.CharField(max_length=30)
    rfid = models.CharField(max_length=200)
    reader_credit = models.IntegerField(max_length=10)
    user_credit = models.IntegerField(max_length=10)
    checkin_date = models.DateTimeField(auto_now_add=True)
    group_average = models.FloatField(max_length=10)
    def __unicode__(self):
        return unicode(self.checkin_date)
    
class Tag(models.Model):
    rfid = models.CharField(max_length=200, unique = True, editable=False)
    alias = models.CharField(max_length=200, unique = True)
    assigned = models.BooleanField()    
    def __unicode__(self):
        return self.rfid
    
class Message(models.Model):
	name = models.CharField(max_length=200)
	content = models.TextField()
	def __unicode__(self):
		return unicode(self.name)    

class Call(models.Model):
	callee = models.CharField(max_length=200)
	message = models.CharField(max_length=200)
	date = models.DateTimeField(auto_now_add=True)
	status = models.IntegerField(default=0)
	def __unicode__(self):
		return unicode(self.id)   
  

class Extra(models.Model):
    for_user = models.CharField(max_length=15)
    description = models.CharField(max_length=30)
    def __unicode__(self):
        return self.description
    
