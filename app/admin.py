# -*- coding: utf-8 -*-
from app.models import User, Site, Category, Story, Msg, Reply, Relationship, Vote
from django.contrib import admin

class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ('nickname','email')

class SiteAdmin(admin.ModelAdmin):
    model = Site
    list_display = ('title','domain')

class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = ('title','name')

class StoryAdmin(admin.ModelAdmin):
    model = Story
    list_display = ('title','karma')

class MsgAdmin(admin.ModelAdmin):
    model = Msg
    list_display = ('title','msg_type', 'date')

class ReplyAdmin(admin.ModelAdmin):
    model = Reply
    list_display = ('title',)
    
class RelationshipAdmin(admin.ModelAdmin):
    model = Relationship
    list_display = ('user_nickname','friend_nickname')

class VoteAdmin(admin.ModelAdmin):
    model = Vote
    list_display = ('value','story_title','msg_title', 'author_nickname')

admin.site.register(User, UserAdmin)
admin.site.register(Site, SiteAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Story, StoryAdmin)
admin.site.register(Msg, MsgAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(Relationship, RelationshipAdmin)
admin.site.register(Vote, VoteAdmin)


