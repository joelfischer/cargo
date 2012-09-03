from cargoapp.models import User, Tag, Message, Call, Checkin, Location, Extra, Game, All_User

from django.contrib import admin

admin.site.register(User)
admin.site.register(Message)
admin.site.register(Tag)
admin.site.register(Call)
admin.site.register(Checkin)
admin.site.register(Location)
admin.site.register(Extra)
admin.site.register(Game)
admin.site.register(All_User)