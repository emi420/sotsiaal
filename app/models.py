# -*- coding: utf-8 *-*
from django.db import models
import app.settings as settings
from django.template.loader import render_to_string

class User(models.Model):
    nickname = models.TextField()
    name = models.TextField(blank=True)
    url = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    location = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="users/",blank=True)    
    background = models.ImageField(upload_to="users/",blank=True)
    banner = models.ImageField(upload_to="users/",blank=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    password = models.TextField()
    recovery_key = models.TextField(blank=True)
    email = models.TextField()
    activation_key = models.TextField(blank=True)
    deletion_key = models.TextField(blank=True)
    deletion_msg = models.TextField(blank=True)
    comments_alerts = models.BooleanField()
    replies_alerts = models.BooleanField()
    invisible_mode = models.BooleanField()
    is_admin = models.BooleanField()
    account_state = models.TextField(blank=True)
    facebook_id = models.TextField(blank=True)
    pop = models.IntegerField()
    unsearchable_properties = [ 'url', 'bio', 'location',  'password', 'recovery_key', 'email','activation_key','deletion_key','deletion_msg','account_state','facebook_id']

class Site(models.Model):
    title = models.TextField()
    domain = models.TextField()

class Category(models.Model):
    title = models.TextField()
    name = models.TextField()
    site = models.ForeignKey('Site')
    
class Story(models.Model):
    author = models.ForeignKey('User')
    title = models.TextField()
    bio = models.TextField(blank=True)
    link = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="stories/", blank=True)
    image = models.ImageField(upload_to="stories/", blank=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    pop = models.IntegerField()
    karma = models.IntegerField()
    hkarma = models.FloatField()
    category = models.ForeignKey('Category')
    site = models.ForeignKey('Site')
    url = models.TextField(blank=True)
    status = models.IntegerField()
    client_ip = models.TextField()
    block_anonymous = models.BooleanField()
    #FIXME (tags support)
    #tags = SeparatedValuesField()

    def generate_path(self):
        '''Generate path to the story.'''
        return '/%s/%s/' % (self.category.name, self.url)

class Msg(models.Model):
    title = models.TextField()
    image = models.ImageField(upload_to="msgs/")
    document = models.TextField(blank=True)
    filename = models.TextField(blank=True)
    video = models.TextField(blank=True)
    map = models.TextField(blank=True)
    map_zoom = models.IntegerField(null=True)
    author = models.ForeignKey('User')
    date = models.DateTimeField(auto_now_add=True, blank=True)
    pop = models.IntegerField()
    storyparent = models.ForeignKey('Story')
    status = models.IntegerField()
    msg_type = models.TextField()
    client_ip = models.TextField()

class Reply(models.Model):
    author = models.ForeignKey('User')
    title = models.TextField()
    date = models.DateTimeField(auto_now_add=True, blank=True)
    replyto = models.ForeignKey('Msg')
    replytor = models.ForeignKey('self', null=True, blank=True)
    has_replies = models.BooleanField()
    pop = models.IntegerField()
    status = models.IntegerField()
    client_ip = models.TextField()

    def sub_replies_html(self):
        if self.has_replies:
            replies = [r for r in Reply.all().filter(replytor=self).order_by('date')]
            for r in replies:
                r.context = self.context
            self.sub_replies = replies
        else:
            self.sub_replies = []

        context = dict((k,v) for k,v in self.context.items())
        context['parent_reply'] = self

        return render_to_string('sitio/sub_replies.html', context)

class Relationship(models.Model):
    user = models.ForeignKey('User', related_name='+')
    friend = models.ForeignKey('User', related_name='+')
    date = models.DateTimeField(auto_now_add=True, blank=True)

class Vote(models.Model):
    date = models.DateTimeField(auto_now_add=True, blank=True)
    author = models.ForeignKey('User')
    story = models.ForeignKey('Story',null=True)
    msg = models.ForeignKey('Msg',null=True)
    reply = models.ForeignKey('Reply',null=True)
    value = models.IntegerField()
