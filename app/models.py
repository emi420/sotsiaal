# -*- coding: utf-8 *-*
from django.db import models
import app.settings as settings
#from django.template.loader import render_to_string

class SeparatedValuesField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ',')
        super(SeparatedValuesField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value: return
        if isinstance(value, list):
            return value
        return value.split(self.token)

    def get_db_prep_value(self, value):
        if not value: return
        assert(isinstance(value, list) or isinstance(value, tuple))
        return self.token.join([unicode(s) for s in value])

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)

class User(models.Model):
    nickname = models.TextField()
    name = models.TextField()
    url = models.TextField()
    bio = models.TextField()
    location = models.TextField()
    avatar_big = models.ImageField(upload_to="users/")
    avatar = models.ImageField(upload_to="users/")
    avatar_med = models.ImageField(upload_to="users/")
    avatar_mini = models.ImageField(upload_to="users/")
    background = models.ImageField(upload_to="users/")
    banner = models.ImageField(upload_to="users/")
    date = models.DateTimeField(auto_now_add=True, blank=True)
    password = models.TextField()
    #googleuser = db.UserProperty()
    recovery_key = models.TextField()
    email = models.TextField()
    activation_key = models.TextField()
    deletion_key = models.TextField()
    deletion_msg = models.TextField()
    comments_alerts = models.BooleanField()
    replies_alerts = models.BooleanField()
    invisible_mode = models.BooleanField()
    is_admin = models.BooleanField()
    account_state = models.TextField()
    facebook_id = models.TextField()
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
    bio = models.TextField()
    link = models.TextField()
    avatar = models.ImageField(upload_to="stories/")
    image = models.ImageField(upload_to="stories/")
    date = models.DateTimeField(auto_now_add=True, blank=True)
    pop = models.IntegerField()
    karma = models.IntegerField()
    hkarma = models.FloatField()
    category = models.ForeignKey('Category')
    site = models.ForeignKey('Site')
    url = models.TextField()
    status = models.IntegerField()
    client_ip = models.TextField()
    block_anonymous = models.BooleanField()
    tags = SeparatedValuesField()

    def generate_path(self):
        '''Generate path to the story.'''
        return '/%s/%s/' % (self.category.name, self.url)


class Msg(models.Model):
    def _get_mime_type(self):
        import mimetypes
        tupla = mimetypes.guess_type(self.filename)
        return tupla[0]
    def _get_file_size(self):
        def sizeof_fmt(num):
            for x in ['bytes','KB','MB','GB','TB']:
                if num < 1024.0:
                    return "%3.1f%s" % (num, x)
                num /= 1024.0
        return sizeof_fmt(len(self.document))

    title = models.TextField()
    image = models.ImageField(upload_to="msgs/")
    document = models.TextField()
    filename = models.TextField()
    mime_type = property(_get_mime_type)
    file_size = property(_get_file_size)
    video = models.TextField()
    map = models.TextField()
    map_zoom = models.IntegerField()
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
    replytor = models.ForeignKey('self')
    has_replies = models.BooleanField()
    pop = models.IntegerField()
    status = models.IntegerField()
    client_ip = models.TextField()

    def sub_replies_html(self):
        if self.has_replies:
            replies = [r for r in Reply.all().filter('replytor =', self).order('date')]
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
    story = models.ForeignKey('Story')
    msg = models.ForeignKey('Msg')
    reply = models.ForeignKey('Reply')
    value = models.IntegerField()
