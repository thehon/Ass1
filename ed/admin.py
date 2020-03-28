from django.contrib import admin
from . models import Profile, Course, Resource, Message, ChatMembership, Group, Comment

# Register your models here.
admin.site.register(Profile)
admin.site.register(Course)
admin.site.register(Resource)
admin.site.register(Message)
admin.site.register(ChatMembership)
admin.site.register(Group)
admin.site.register(Comment)