from cargoapp.models import User, Tag, Message, Call, Checkin

from django.contrib import admin

admin.site.register(User)
admin.site.register(Message)
admin.site.register(Tag)
admin.site.register(Call)
admin.site.register(Checkin)