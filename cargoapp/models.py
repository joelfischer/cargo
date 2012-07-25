from django.db import models

class User(models.Model):
    name = models.CharField(max_length=15)
    phone_num = models.CharField(max_length=30)
    group = models.CharField(max_length=30)
    alias = models.CharField(max_length=30)
    rfid = models.CharField(max_length=200)
    def __unicode__(self):
        return self.name

class Checkin(models.Model):
    location = models.CharField(max_length=200)
    rfid = models.CharField(max_length=200)
    checkin_date = models.DateTimeField(auto_now_add=True)
    displayed = models.BooleanField()
    def __unicode__(self):
        return unicode(self.checkin_date)
    
<<<<<<< HEAD
class Tag(models.Model):
    rfid = models.CharField(max_length=200, unique = True)
    alias = models.CharField(max_length=200, unique = True)
    assigned = models.BooleanField()    
    def __unicode__(self):
        return self.rfid
    
    
=======
class Message(models.Model):
	name = models.CharField(max_length=200)
	content = models.CharField(max_length=50)
	def __unicode__(self):
		return unicode(self.name)
>>>>>>> Added basic Calls view functionality
