import datetime
import hashlib
import re
import random
import urllib2
import logging
import cgi

from os import environ

#from google.appengine.ext import db
#from google.appengine.api import mail, images
#import google.appengine.api.images
#from google.appengine.api import memcache
#from google.appengine.ext import blobstore
#from google.appengine.api import urlfetch
#from google.appengine.api import users

from django import forms
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseForbidden
from django.core.paginator import Paginator
from django.utils import simplejson
from django.utils.http import urlquote
#from django.conf import settings
from django.template.loader import render_to_string
from django.template import RequestContext

from app.models import User, Category, Story, Msg, Reply, Relationship, Vote, Site
from app.utils import *
#from app.facebook import Facebook
from app import captcha
#from app import blobstore_helper


# sidebar styles
SIDEBAR_NONE = 0
SIDEBAR_BASIC = 1
SIDEBAR_PROFILE = 2
SIDEBAR_NOAD = 3

MESSAGES_ON_PAGE = 100
STORIES_ON_PAGE = 15

class Mail:
    def is_email_valid(self, email):
        f = forms.EmailField()
        return f.clean(email)

mail = Mail()

def add_common_context(request, context, title = '', description = '', sidebar_style = SIDEBAR_NONE, user_profile = ''):
    '''Fill context with common values.'''
    # FIXME check, is migrated code

    # m_Header
    context['title'] = title
    context['desc'] = description
    context['userprofile'] = user_profile

    # m_SideBar
    if 'logged_user' in request.session:
        user = get_current_user(request)
    else:
        user = ''

    followers = []
    followers_count = None
    classname = ''

    if sidebar_style == SIDEBAR_BASIC:
        classname = 'inner-sidebar'
    elif sidebar_style == SIDEBAR_PROFILE:
        # user profile
        classname = 'inner-sidebar profile'
        following_query = Relationship.objects.get(friend=user_profile)
        followers_count = following_query.count()
        followers = following_query.fetch(20)
    elif sidebar_style == SIDEBAR_NOAD:
        classname = 'inner-sidebar noad'
    else:
        # general
        # FIXME what classname?
        pass

    context['classname'] = classname
    context['user'] = user
    context['followers'] = followers
    context['followers_count'] = followers_count

    # m_Footer
    context['urlback'] = urlquote(request.path)

def add_stories_context(request, context, stories):
    '''Fill context with stories values.'''
    # FIXME check, migrated code

    # Paginator
    if 'page' in request.GET:
        page = request.GET.get('page', '')
    else:
        page = 1

    paginator = Paginator(stories, STORIES_ON_PAGE)
    try:
        stories_paginated = paginator.page(int(page)).object_list
        pages = paginator.page_range
        page_count = paginator.num_pages + 1
    except:
        pages = []
        page_count = 2
        stories_paginated = []

    # Info, url, comments
    for story in stories_paginated:
        msgs = Msg.objects.filter(storyparent=story)
        story.comments = msgs.count()
        story.shortdesc = story.bio[0:140]

    context['stories'] = stories_paginated
    context['pages'] = pages
    context['pageprev'] = int(page)-1
    context['pagenext'] = int(page)+1
    context['pagecount'] = page_count

def messages_paginated(story, page, context):
    '''Get story messages paginated.'''
    messages = Msg.objects.filter(storyparent=story).order_by('date')
    now = datetime.datetime.today()

    # Paginator
    paginator = Paginator(messages, MESSAGES_ON_PAGE)
    try:
        msgs = paginator.page(page).object_list
    except:
        msgs = []

    if msgs:
        # messages
        for m in msgs:
            if m.pop < -10:
                m.classname = 'hidden'
            if m.pop > 0:
                m.popsign = '+'
            if m.status == 1:
                m.classname = 'hidden'
            tafmsd = datetime.datetime(m.date.year, m.date.month, m.date.day, m.date.hour, m.date.minute, m.date.second)
            difference = now - tafmsd
            formated_difference = get_formated_time(difference)
            m.difference = formated_difference[0]
            m.difference_unit = formated_difference[1]
            if m.msg_type == 'video':
                m.video = m.video.replace('/watch?','/')
                m.video = m.video.replace('=','/')
            # answers
            msgs2 = [r for r in Reply.objects.filter(replyto=m).order_by('date')]
            m.replies = msgs2
            for r in m.replies:
                if r.pop > 0:
                    r.popsign = '+'
                if r.pop < -10:
                    r.classname = 'hidden'
                tafmsd = datetime.datetime(r.date.year, r.date.month, r.date.day, r.date.hour, r.date.minute, r.date.second)
                difference = now - tafmsd
                formated_difference = get_formated_time(difference)
                r.difference = formated_difference[0]
                r.difference_unit = formated_difference[1]

                r.context = context
    return msgs

@internal_login_required
def index(request, category_name = ''):
    '''Home page.'''
    context = {}

    if 'popular' in request.GET:
        period = int(request.GET.get('popular', ''))
        difference = datetime.timedelta(days=-period)
        datelimit = datetime.datetime.now() + difference

    site = Site.objects.get(domain=settings.SITE_DOMAIN)

    # Category filter
    if category_name:
        category = Category.objects.filter(name=category_name)[0]

        #stories = memcache.get('category_stories_' + category_name)
        stories = None 
        if not stories:
            if category:
                stories = Story.objects.filter(status=0,category=category).order_by('-karma')
            else:
                stories = []
            #memcache.set('category_stories_' + category_name, list(stories), 60)

        add_common_context(request, context, category_name.capitalize())
        context['show_box_welcome'] = False
        context['feed_url'] = '/feeds/categories/%s/' % category_name
    else:
        # Date filter
        if 'popular' in request.GET:
            context['is_home'] = '1'
            stories = Story.objects.filter(status=0,date__gte=datelimit).order_by('date').order_by('-karma')
        else:
            # All (home)
            user = get_current_user(request)
            context['user'] = user
            context['urlback'] =  '/'
            context['userprofile'] = ''
            context['is_home'] = '1'
            
            #stories = memcache.get('home_stories')
            stories = Story.objects.filter(status=0,site=site).order_by('data').order_by('hkarma')
            #memcache.set('home_stories', list(stories), 60)

        add_common_context(request, context)
        context['show_box_welcome'] = True
        context['feed_url'] = '/feeds/stories/'

    add_stories_context(request, context, stories)

    categories = Category.objects.filter(site=site).order_by('name')
    context['categories'] = categories

    context['name'] = category_name
    context['userprofile'] = ''
    context['categoryname'] = category_name
    context['popular'] = request.GET.get('popular', '')
    return render_to_response('sitio/index.html', context, context_instance=RequestContext(request))

@internal_login_required
def story(request, category_key, story_url):
    '''Story page.'''
    # FIXME check, is migrated code
    context = {}
    user = get_current_user(request)
    context['user'] = user
    context['urlback'] =  urlquote(('/' + category_key + '/' + story_url + '/'))

    #story = memcache.get('story_' + story_url)
    story = None
    if not story:
        story = Story.objects.get(url=urlquote(story_url))
        #memcache.set('story_' + story_url, story, 60)

    if story and (not story.status or (user and user.is_admin)) and story.site == request.session['site']:
        if story.author.background:
            add_common_context(request, context, story.title, user_profile = story.author,  sidebar_style = SIDEBAR_BASIC)
        else:
            add_common_context(request, context, story.title.replace(',','') + ',' + story.bio.replace(',',''),  sidebar_style = SIDEBAR_BASIC)

        # story date
        now = datetime.datetime.today()
        tafmsd = datetime.datetime(story.date.year, story.date.month, story.date.day, story.date.hour, story.date.minute, story.date.second)
        difference = now - tafmsd
        current_user = get_current_user(request)
        formated_difference = get_formated_time(difference)

        # follow story's author
        following_query = Relationship.objects.filter(user=current_user,friend=story.author)
        following = following_query.count()

        usr_voted = Vote.objects.filter(author=get_current_user(request),story=story,value__gte=0)[0]
        usr_buried = Vote.objects.filter(author=get_current_user(request),story=story,value__gte=0)[0]

        storytitle = story.title + ' - '

        #TODO
        #related_stories = stories = Story.filter('status =', 0).search(story.title)[:5]
        #related_stories = [s for s in related_stories if s.key() != story.key()]
        related_stories = [];
        
        allow_comments = True
        try:
            if story.block_anonymous:
                if not user or user.invisible_mode:
                    allow_comments = False
        except:
            pass
            

        
        context['allow_comments'] = allow_comments
        chtml = ''
        user = get_current_user(request) 
        if user:
    	    context['is_anon'] = '0'
        else:
            context['is_anon'] = '1'
            chtml = captcha.displayhtml(
            public_key = settings.RECAPTCHA_KEY,
              use_ssl = False,
              error = None)

        context['captchahtml'] = chtml
        context['enable_bigfiles'] = settings.ENABLE_BIGFILES
        context['uploadurl'] = blobstore.create_upload_url('/upload_blob/')        
        context['story'] = story
        context['error'] = request.GET.get('error', '')
        context['sidebar_stories'] = related_stories
        context['sidebar_stories_title'] = settings.DEFAULT_SIDEBAR_STORIES_TITLE
        context['storytitle'] = storytitle
        context['usrvoted'] = usr_voted
        context['usrburied'] = usr_buried
        context['following'] = following
        if story.author.email == settings.ANONYMOUS_USER_MAIL:
            context['difference'] = 0
        else:
            context['difference'] = formated_difference[0]
        context['difference_unit'] = formated_difference[1]
        context['page'] = 2
        context['default_comment_text'] = settings.DEFAULT_COMMENT_TEXT
        context['msg'] = request.GET.get('msg', '')
        context['title'] = story.title
        context['desc'] = story.bio
        context['load_gmaps'] = '1'

        messages = messages_paginated(story, 1, context)
        context['msgs'] = messages
        context['more_msgs_link'] = len(messages) == MESSAGES_ON_PAGE

        return render_to_response('sitio/story.html', context, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/invalid_story/')

			
@internal_login_required
def print_story(request, story_key):
    '''Print story.'''
    context = {}
    story = Story.objects.get(id=story_key)
    context['story'] = story
    return render_to_response('sitio/story_print.html', context,
                              context_instance=RequestContext(request))

@internal_login_required
def legal(request):
    '''Legal info page.'''
    context = {}
    add_common_context(request, context, 'T&eacute;rminos y condiciones',
                       sidebar_style = SIDEBAR_NOAD)

    return render_to_response('sitio/legal.html', context,
                              context_instance=RequestContext(request))

def contact(request):
    '''Legal info page.'''
    context = {}
    add_common_context(request, context, 'Formulario de contacto')

    context['error'] = request.GET.get('error', '')

    return render_to_response('sitio/contact.html', context,
                              context_instance=RequestContext(request))

@internal_login_required
def search(request):
    '''Search page.'''
    # FIXME check, is migrated code
    context = {}
    add_common_context(request, context, request.GET.get('q', ''),
                       sidebar_style = SIDEBAR_BASIC)

    searchquery = request.GET.get('q', '').upper()
    
    #TODO
    #stories1 = Story.filter('status =', 0).search(searchquery)
    stories1 = []
    #users = User.all().search(searchquery)
    users = []
    #stories2 = Story.filter('status =', 0).filter('author IN',[u.key() for u in users])
    stories2 = []
    #stories = Story.filter('__key__ IN',[u.key() for u in stories1] + [u.key() for u in stories2])
    stories = []
    
    add_stories_context(request, context, stories)

    context['searchquery'] = request.GET.get('q', '')

    return render_to_response('sitio/search.html', context,
                              context_instance=RequestContext(request))

@internal_login_required
def new_story(request):
    '''New Story page.'''
    get_title = request.GET.get('title', '')
    get_desc = request.GET.get('desc', '')
    get_url = request.GET.get('url', '')
    get_feed = request.GET.get('feed', '')
    chtml = ''
	
    if get_url != '':
	    return HttpResponseRedirect('/')
    context = {}
    add_common_context(request, context, sidebar_style = SIDEBAR_NOAD)

    categories = Category.objects.all().order_by('name')
    error = request.GET.get('error', '')
	
    user = get_current_user(request) 
    if user:
	    context['is_anon'] = '0'
    else:
        context['is_anon'] = '1'
        chtml = captcha.displayhtml(
        public_key = settings.RECAPTCHA_KEY,
          use_ssl = False,
          error = None)

    
    context['banner_no_button'] = '1'
    context['captchahtml'] = chtml
    context['categories'] = categories
    context['error'] = error
    context['get_title'] = get_title
    context['get_desc'] = get_desc
    context['get_url'] = get_url	
    context['get_feed'] = get_feed

    return render_to_response('sitio/new_story.html', context,
                              context_instance=RequestContext(request))

def login(request):
    '''Login page.'''
    context = {}
    add_common_context(request, context, sidebar_style = SIDEBAR_NOAD)

    context['urlback'] = urlquote(request.GET.get('urlback', ''))
    context['error'] = request.GET.get('error', '')
    context['is_home'] = '1'
    context['allowed_user_domains'] = settings.ALLOWED_USER_DOMAINS
	
    return render_to_response('sitio/login.html', context,
                              context_instance=RequestContext(request))

def signup(request):
    '''Sign up page.'''
    context = {}
    add_common_context(request, context, sidebar_style = SIDEBAR_NOAD)

    error = request.GET.get('error', '')
    context['urlback'] = urlquote(request.GET.get('urlback', ''))
    context['error'] = error
    context['allowed_user_domains'] = settings.ALLOWED_USER_DOMAINS

    return render_to_response('sitio/signup.html', context,
                              context_instance=RequestContext(request))

@login_required
def edit_profile(request):
    '''Edito profile page.'''
    context = {}
    add_common_context(request, context, sidebar_style = SIDEBAR_NOAD)

    context['error'] = request.GET.get('error', '')

    return render_to_response('sitio/edit_profile.html', context,
                              context_instance=RequestContext(request))

@internal_login_required
def view_profile(request, user_nickname):
    '''User profile page.'''
    context = {}

    #view_user = memcache.get('user_' + user_nickname)
    view_user = None
    if not view_user:
        try:
            view_user = User.objects.filter(nickname=user_nickname)[0]
        except:
            pass
        #memcache.set('user_' + user_nickname, view_user, 60)

    if view_user:
        if view_user.background:

            add_common_context(request, context, user_nickname,
                           user_profile = view_user,
                           sidebar_style = SIDEBAR_PROFILE)
    else:
        add_common_context(request, context, user_nickname,
                           sidebar_style = SIDEBAR_PROFILE)

    # FIXME check, is migrated code
    user = get_current_user(request)

    # published stories
    stories = Story.objects.filter(status=0,author=view_user).order_by('-date')

    stories_count = stories.count()

    add_stories_context(request, context, stories)

    # followers
    followers_query = Relationship.filter(friend=view_user) 
    followers = followers_query.fetch(20)

    following_query = Relationship.filter(friend=view_user,user=user)
    following = following_query.count()

    context['user'] = user
    context['viewuser'] = view_user
    context['followers'] = followers
    context['following'] = following
    context['stories_count'] = stories_count
    if view_user.email[view_user.email.find('@') + 1 : len(view_user.email)]  == request.session['site'].domain:
        return render_to_response('sitio/view_profile.html', context,
	                              context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/')

def pass_recovery(request):
    '''Pass recovery page.'''
    context = {}
    add_common_context(request, context,
                       sidebar_style = SIDEBAR_NOAD)

    rkey = request.GET.get('rkey', '')
    context['rkey'] = rkey
    context['error'] = request.GET.get('error', '')

    return render_to_response('sitio/pass_recovery.html', context,
                              context_instance=RequestContext(request))

@login_required
@admin_required
def admin(request):
    '''Admin page.'''
    context = {}
    add_common_context(request, context, sidebar_style = SIDEBAR_NOAD)

    return render_to_response('sitio/admin.html', context,
                              context_instance=RequestContext(request))

@login_required
@admin_required
def admin_categories(request):
    '''Categories admin page.'''
    context = {}
    add_common_context(request, context, sidebar_style = SIDEBAR_NOAD)

    categories = Category.all()
    context['categories'] = categories

    return render_to_response('sitio/admin_categories.html', context,
                              context_instance=RequestContext(request))

@login_required
@admin_required
def admin_sites(request):
    '''Categories admin page.'''
    context = {}
    add_common_context(request, context, sidebar_style = SIDEBAR_NOAD)

    sites = Site.all()
    context['sites'] = sites

    return render_to_response('sitio/admin_sites.html', context,
                              context_instance=RequestContext(request))


@login_required
@admin_required
def admin_users(request):
    '''Users admin page.'''
    context = {}
    add_common_context(request, context, sidebar_style = SIDEBAR_NOAD)

    searchquery = request.GET.get('q', '').upper()
    if searchquery:
        users = User.all().search(searchquery)
    else:
        users = User.all()

    if 'page' in request.GET:
        page = request.GET.get('page', '')
    else:
        page = 1

    paginator = Paginator(users, 20)
    try:
        users_paginated = paginator.page(int(page)).object_list
        pages = paginator.page_range
        page_count = paginator.num_pages + 1
    except:
        users_paginated = []
        pages = []
        page_count = 2

    context['users'] = users_paginated
    context['userssearchquery'] = request.GET.get('q', '')
    context['pages'] = pages
    context['pageprev'] = int(page)-1
    context['pagenext'] = int(page)+1
    context['pagecount'] = page_count

    return render_to_response('sitio/admin_users.html', context,
                              context_instance=RequestContext(request))

@login_required
@admin_required
def block_user(request, userkey):
    '''Do account blocking.'''
    usr = User.objects.get(id=userkey)
    if usr:
        usr.account_state = 'blocked'
        usr.save()

    urlback = request.GET.get('urlback', '/admin/users/')
    return HttpResponseRedirect(urlback)

@login_required
@admin_required
def enable_user(request, userkey):
    '''Do account re enabling.'''
    usr = User.objects.get(id=userkey)
    if usr:
        usr.account_state = ''
        usr.save()

    urlback = request.GET.get('urlback', '/admin/users/')
    return HttpResponseRedirect(urlback)

@login_required
@admin_required
def block_story(request, storykey):
    '''Do story blocking.'''
    story = Story.objects.get(id=storykey)
    if story:
        story.status = 1
        story.save()

    return HttpResponseRedirect(story.generate_path())

@login_required
def delete_story(request, storykey):
    '''Do story deletion.'''
    story = Story.objects.get(id=storykey)
    user = get_current_user(request)
    if story and story.author.id == user.id:
        story.status = 1
        story.save()
    context = {}
    add_common_context(request, context, sidebar_style = SIDEBAR_NOAD)

    context['urlback'] = '/'
    return render_to_response('sitio/deleted_story.html', context, context_instance=RequestContext(request))
@login_required
@admin_required
def enable_story(request, storykey):
    '''Do story re enabling.'''
    story = Story.objects.get(id=storykey)
    if story:
        story.status = 0
        story.save()

    return HttpResponseRedirect(story.generate_path())

@login_required
@admin_required
def enable_message(request, msgkey):
    '''Do message re enabling.'''
    msg = Msg.objects.get(id=msgkey)
    if msg:
        msg.status = 0
        msg.save()

    return HttpResponseRedirect(msg.storyparent.generate_path())

@login_required
@admin_required
def enable_reply(request, replykey):
    '''Do reply re enabling.'''
    reply = Reply.objects.get(id=replykey)
    if reply:
        reply.status = 0
        reply.save()

    return HttpResponseRedirect(reply.replyto.storyparent.generate_path())

@login_required
@admin_required
def hard_delete_message(request, msgkey):
    '''Do message hard deletting.'''
    urlback = '/'
    msg = Msg.objects.get(id=msgkey)
    if msg:
        urlback = msg.storyparent.generate_path()
        msg.delete()

    return HttpResponseRedirect(urlback)

@login_required
@admin_required
def hard_delete_reply(request, replykey):
    '''Do reply hard deletting.'''
    urlback = '/'
    reply = Reply.objects.get(id=replykey)
    if reply:
        urlback = reply.replyto.storyparent.generate_path()
        reply.delete()

    return HttpResponseRedirect(urlback)

@login_required
@admin_required
def banned_stories(request):
    '''Banned stories admin page.'''
    context = {}
    add_common_context(request, context, sidebar_style = SIDEBAR_NOAD)

    stories = Story.filter(status=1).order_by('-date')
    context['stories'] = stories

    return render_to_response('sitio/banned_stories.html', context,
                              context_instance=RequestContext(request))

def add_user(request):
    '''Add user action.'''
    # FIXME check, is migrated code for POST method

    if request.POST.get('nickname', '') and \
       (any([request.POST.get('email', '').endswith(domain)
            for domain in settings.ALLOWED_USER_DOMAINS]) or \
       settings.SITE_MODE == settings.SITE_MODE_PUBLIC ) and \
       mail.is_email_valid(request.POST.get('email', '')) and \
       request.POST.get('password', ''):
        if request.POST.get('password', '') == request.POST.get('rpassword', ''):
            prevuser = None
            try:
                prevuser = User.objects.get(nickname=request.POST.get('nickname', ''))
            except:
                pass
            if prevuser == None:
                usr = User()
                usr.bio = ''
                usr.name = ''
                usr.location = ''
                usr.url = ''
                usr.nickname = request.POST.get('nickname', '')
                usr.email = request.POST.get('email', '')
                usr.password =  hashlib.md5(request.POST.get('password', '')).hexdigest()
                usr.is_admin = False
                usr.comments_alerts = True
                usr.replies_alerts = True
                usr.pop = 0

                if settings.USE_MAIL_ACTIVATION:
                    usr.activation_key = hashlib.md5(str(random.random())).hexdigest()
                else:
                    usr.activation_key = ''

                usr.save()

                if settings.USE_MAIL_ACTIVATION:
                    return HttpResponseRedirect('/send_activation_mail/%s/' % str(usr.id))
                else:
                    request.session['logged_user'] = str(usr.id)
                    return HttpResponseRedirect('/account_message/?message=2')

            else:
                return HttpResponseRedirect('/signup/?error=1') # already existent user
        else:
            return HttpResponseRedirect('/signup/?error=3') # password missmatch
    else:
    	if (any([request.POST.get('email', '').endswith(domain)
            for domain in settings.ALLOWED_USER_DOMAINS])):
        	return HttpResponseRedirect('/signup/?error=2') # required field missing
        else:
        	return HttpResponseRedirect('/signup/?error=4') # required field missing

def do_login(request):
    '''Do login.'''
    # FIXME check, is migrated code for POST method

    urlback = request.POST.get('urlback', '/')

    if request.POST.get('email', ''):
        if request.POST.get('password', ''):
            usr = None
            try:
                usr = User.objects.filter(email=request.POST.get('email', ''), password=hashlib.md5(request.POST.get('password', '')).hexdigest())[0]
            except:
                pass
            if usr:
                if usr.activation_key:
                    # user not activated
                    return HttpResponseRedirect('/account_message/?message=5')
                elif usr.account_state == 'deleted':
                    # deleted account
                    return HttpResponseRedirect('/account_message/?message=10')
                elif usr.account_state == 'blocked':
                    # blocked account
                    return HttpResponseRedirect('/account_message/?message=11')
                elif usr.facebook_id:
                    # trying to login with a facebook account
                    return HttpResponseRedirect('/login/?error=1&urlback=%s' % urlback)
                else:
                    # user session initialization
                    request.session['logged_user'] = str(usr.id)

                    return HttpResponseRedirect(urlback)# login ok, go to urlback
            else:
                return HttpResponseRedirect('/login/?error=1&urlback=%s' % urlback) # invalid user/password
        else:
            return HttpResponseRedirect('/login/?error=2&urlback=%s' % urlback) # missing password
    else:
        return HttpResponseRedirect('/login/?error=3&urlback=%s' % urlback) # missing user name

def login_facebook_connect(request):
    '''Do facebook connect login.'''
    try:
        expires = request.GET.get('expires', '')
        ss = request.GET.get('ss', '')
        session_key = request.GET.get('session_key', '')
        facebook_id = request.GET.get('user', '')
        sig = request.GET.get('sig', '')
        urlback = request.GET.get('urlback', '/')

        pre_hash_string = "expires=%ssession_key=%sss=%suser=%s%s" % (
            expires,
            session_key,
            ss,
            facebook_id,
            settings.FACEBOOK_APPLICATION_SECRET,
        )
        post_hash_string = hashlib.new('md5')
        post_hash_string.update(pre_hash_string)
        if post_hash_string.hexdigest() == sig:
            usr = User.objects.filter(facebook_id=facebook_id)[0]
            if not usr:
                facebook = Facebook(settings.FACEBOOK_API_KEY, settings.FACEBOOK_APPLICATION_SECRET)
                info = facebook.users.getStandardInfo([facebook_id],
                                                      ['name',
                                                       'proxied_email',
                                                       'first_name',
                                                       'last_name',
                                                       'profile_url',
                                                       'current_location'])[0]
                nickname = info['name']

                usr2 = User.filter(nickname=nickname)[0]
                if usr2:
                    # facebook user with same name of a stq user
                    return HttpResponseRedirect('/login/?error=5&urlback=%s' % urlback)
                else:
                    # new facebook user
                    usr = User()
                    usr.facebook_id = facebook_id
                    usr.nickname = nickname
                    usr.email = info['proxied_email'] or ''; # is there another way?
                    usr.name = (info['first_name'] or '') + ' ' + (info['last_name'] or '')
                    usr.url = info['profile_url'] or ''
                    usr.location = info['current_location'] or ''
                    usr.bio = ''
                    usr.pop = 0
                    usr.save()

            if usr.account_state == 'blocked':
                # blocked account
                return HttpResponseRedirect('/account_message/?message=11')
            else:
                request.session['logged_user'] = str(usr.id)
                return HttpResponseRedirect(urlback)# login ok, go to urlback
        else:
            return HttpResponseRedirect('/login/?error=6&urlback=%s' % urlback)

    except Exception, e:
        return HttpResponseRedirect('/login/?error=6&urlback=%s' % urlquote(urlback))

@login_required
def logout(request):
    '''Do logout.'''
    # clean user session

    if 'logged_user' in request.session:
        del request.session['logged_user']
    if 'site' in request.session:
        del request.session['site']
    if 'urlback' in request.GET:
        return HttpResponseRedirect( users.create_logout_url(urlquote(request.GET.get('urlback', ''))) ) # logout ok, go to urlback
    else:
        return HttpResponseRedirect( users.create_logout_url(urlquote(request.GET.get('/', ''))) ) # logout ok, go to urlback

@logged_or_fail
def save_profile(request):
    '''Save profile.'''
    # FIXME check, is migrated code for POST method
    error = 0
    user = get_current_user(request)
    if 'img' in request.FILES:
        try:
            image = request.FILES['img'].read()
            #TODO
            user.avatar = '' #db.Blob(images.resize(image, 49, 49))
            user.avatar_big = '' #db.Blob(image)
            user.avatar_mini = '' #db.Blob(images.resize(image, 16, 16))
            user.avatar_med = '' #db.Blob(images.resize(image, 128, 128))
        except:
            return HttpResponseRedirect('/edit_profile/?error=1') # image error, possibly a too big file
    if 'imgbg' in request.FILES:
        try:
            #TODO
            user.background = '' #db.Blob(request.FILES['imgbg'].read())
        except:
            return HttpResponseRedirect('/edit_profile/?error=1') # image error, possibly a too big file
    if 'imgbanner' in request.FILES:
        try:
            #TODO
            user.banner = '' #db.Blob(request.FILES['imgbanner'].read())
        except:
            return HttpResponseRedirect('/edit_profile/?error=1') # image error, possibly a too big file
    #if request.POST.get('nickname', ''):
    #    user.nickname = request.POST.get('nickname', '')
    user.name = request.POST.get('name', '')
    user.bio = request.POST.get('bio', '')
    user.url = request.POST.get('url', '')
    if user.url and not user.url.strip().startswith('http'):
        user.url = 'http://' + user.url.strip()
    user.location = request.POST.get('location', '')
    user.comments_alerts = 'comments_alerts' in request.POST
    user.replies_alerts = 'replies_alerts' in request.POST
    user.invisible_mode = 'invisible_mode' in request.POST

    try:
        user.save()
        return HttpResponseRedirect('/edit_profile/?error=0') # saved profile
    except:
        return HttpResponseRedirect('/edit_profile/?error=1') # image error, possibly a too big file

def save_pass(request):
    '''Save password.'''
    # FIXME check, is migrated code for POST method
    error = 0
    rkey = request.POST.get('rkey', '')
    if rkey:
        user = User.objects.filter(recovery_key=rkey)[0]
    else:
        user = get_current_user(request)

    if user:
        if(request.POST.get('password', '') == request.POST.get('rpassword', '')):
            user.password = hashlib.md5(request.POST.get('password', '')).hexdigest()
            user.save()
            if rkey:
                return HttpResponseRedirect('/pass_recovery/?error=4') # password changed
            else:
                return HttpResponseRedirect('/edit_profile/?error=0') # profile saved
        else:
            if rkey:
                return HttpResponseRedirect('/pass_recovery/?error=3&rkey=' + rkey) # passwords missmatch
            else:
                return HttpResponseRedirect('/edit_profile/?error=2#new-pass') # passwords missmatch
    else:
        if rkey:
            return HttpResponseRedirect('/pass_recovery/?error=3&alt=1&rkey=' + rkey) # passwords missmatch
        else:
            return HttpResponseRedirect('/') # trying to change password without rkey or logged user

@internal_logged_or_fail
def add_story(request):
    '''Add story.'''
    # FIXME check, is migrated code for POST method	
    usr = get_current_user(request)
    challenge = request.POST.get('recaptcha_challenge_field')
    response  = request.POST.get('recaptcha_response_field')
    #TODO
    remoteip  = '' #environ['REMOTE_ADDR']
    cResponse = captcha.submit(
                     challenge,
                     response,
                     settings.RECAPTCHA_PRIVATEKEY,
                     remoteip)

    if cResponse.is_valid or usr:
        if ( usr == None ):
            usr = User.objects.get(email=settings.ANONYMOUS_USER_MAIL)
        story = None
        if request.POST.get('title', '') and request.POST.get('bio', '') and request.POST.get('category', ''):
            # story
            
            story = Story()
            #FIXME CHECK
            story.site = Site.objects.get(domain=settings.SITE_DOMAIN)
            story.client_ip = '' #request.META['REMOTE_ADDR']
		
            story.link = request.POST.get('link', '')
            if ( story.link ):
                 exist_prev_count = None
                 try:
                     exist_prev_query = Story.objects.get(link=story.link)
                     exist_prev_count = exist_prev_query.count()
                 except:
                     pass
                 if exist_prev_count:
                     prev_story = exist_prev_query.get()
                     return HttpResponseRedirect( prev_story.generate_path() + '?msg=1' ) # exist prev history, same title		

            usr = get_current_user(request)
            use_anonymous = False
            if ( usr == None ):
                use_anonymous = True
            else:
                try:
                    if usr.invisible_mode:
                        use_anonymous = True
                except:
                    pass

            if use_anonymous:
                usr = User.objects.get(email=settings.ANONYMOUS_USER_MAIL)
                #story.date = '001-01-01 01:01:01'

            story.author = usr
            story.url = urlquote(request.POST.get('title', '').replace('/', '-').replace(' ', '-').lower())
            story.block_anonymous = 'block_anonymous' in request.POST
            urlprev_query = Story.objects.filter(url=story.url)
            urlprev_count = urlprev_query.count()
            if urlprev_count:
                story.save()
                story.url = story.url + '-' + str(story.id)
            story.title = request.POST.get('title', '')

            story.bio = request.POST.get('bio', '')
            if story.link and not story.link.strip().startswith('http'):
               story.link = 'http://' + story.link.strip()

            category = Category.objects.filter(name=request.POST.get('category', ''))[0]
            story.category = category
            story.pop = 1
            story.karma = 10
            url_img_value = request.POST.get('url_img_value', '')
            if( url_img_value ):
                image = urllib.urlopen(url_img_value).read()
                #TODO
                story.avatar = image #db.Blob(images.resize(image, 78, 78))
                story.image = image #db.Blob(image)
            else:
                if('img' in request.FILES):
                    image = request.FILES['img'].read()
                    #TODO
                    story.avatar = image #db.Blob(images.resize(image, 78, 78))
                    story.image = image #db.Blob(image)
            story.status = 0
            if usr.email == settings.ANONYMOUS_USER_MAIL:
            	story.client_ip = '127.0.0.1'
            	#story.date = settings.ANONYMOUS_DATETIME
            story.save()
            # first vote
            vote = Vote()
            vote.story = story
            vote.author = usr
            vote.value = 1
            vote.save()
            
        if story:
            if usr.email == settings.ANONYMOUS_USER_MAIL:
                return HttpResponseRedirect('/')
            else: 
                return HttpResponseRedirect(story.generate_path()) # story saved
        else:
            rurl = '/new_story/?error=1' 
            return HttpResponseRedirect(rurl)
            # required field missing
    else:
        error = cResponse.error_code
        rurl = '/new_story/?error=2' 
        return HttpResponseRedirect(rurl)

@internal_logged_or_fail
def add_message(request):
    '''Add message.'''
    # FIXME check, is migrated code for POST method
    
    # replies
    title = request.POST.get('title', '')
    
    if 'replyto' in request.POST:
        key_name = request.POST.get('replyto', '')
        msg = Msg.objects.get(id=key_name)
		
        usr = get_current_user(request)
        use_anonymous = False
        
        if ( usr == None ):
            usr = User.objects.get(email=settings.ANONYMOUS_USER_MAIL)
            remoteip  = environ['REMOTE_ADDR']
            use_anonymous = True
        else:
            try:
                if usr.invisible_mode:
                    use_anonymous = True
            except:
                pass
            
        if use_anonymous:
            if settings.SITE_MODE != settings.SITE_MODE_PUBLIC:
                usr = User.objects.get(email=settings.ANONYMOUS_USER_MAIL)
            else:
                title = None
		
        if title and title != settings.DEFAULT_COMMENT_TEXT:
            reply = Reply()
            if usr.email == settings.ANONYMOUS_USER_MAIL:
            	reply.client_ip = '127.0.0.1'
            	#reply.date = settings.ANONYMOUS_DATETIME
            else:
                reply.client_ip = request.META['REMOTE_ADDR']
            reply.replyto = msg
            reply.author = usr
            reply.title = request.POST.get('title', '')

            reply.pop = 0
            reply.save()

            # karma
            msg.storyparent.karma += 1
            msg.storyparent.save()
			
            if settings.ENABLE_MAIL_ALERTS and msg.author.replies_alerts and \
               not msg.author.account_state and msg.author.email and \
               mail.is_email_valid(msg.author.email):
                # send mail alert about the reply
                sender_adress = settings.SITE_MAIL
                receiver_address = msg.author.email
                subject = 'Te han respondido a un mensaje'
                body = render_to_string('sitio/mail_comment_response.html',
                                        {'title': msg.storyparent.title,
                                         'link': msg.storyparent.generate_path()})
                mail.send_mail(sender_adress, receiver_address, subject, body)

        return HttpResponseRedirect(msg.storyparent.generate_path())
        
    # sub replies
    elif 'replytor' in request.POST:
        key_name = request.POST.get('replytor', '')
        parent_reply = db.get(db.Key(key_name))
		
        parent_story = parent_reply
        search = True
        while search:
            if parent_story.replytor:
                parent_story = parent_story.replytor
            elif parent_story.replyto:
                parent_story = parent_story.replyto.storyparent
                search = False

        usr = get_current_user(request)

        use_anonymous = False
        if ( usr == None ):
            use_anonymous = True
        else:
            try:
                if usr.invisible_mode:
                    use_anonymous = True
            except:
                pass

        if use_anonymous:
            if settings.SITE_MODE != settings.SITE_MODE_PUBLIC:
                usr = User.objects.get(email=settings.ANONYMOUS_USER_MAIL)
            else:
                title = None
		
        if title and title != settings.DEFAULT_COMMENT_TEXT:
            reply = Reply()
            if usr.email == settings.ANONYMOUS_USER_MAIL:
            	reply.client_ip = '127.0.0.1'
            	#reply.date = settings.ANONYMOUS_DATETIME
            else:
                reply.client_ip = request.META['REMOTE_ADDR']
            reply.replytor = parent_reply
            reply.author = usr
            reply.title = request.POST.get('title', '')

            reply.pop = 0
            reply.save()

            parent_reply.has_replies = True
            parent_reply.save()

            # karma
            #msg.storyparent.karma += 1
            #msg.storyparent.save()
			
            if settings.ENABLE_MAIL_ALERTS and reply.author.replies_alerts and \
               not reply.author.account_state and reply.author.email and \
               mail.is_email_valid(parent_reply.author.email):
                # send mail alert about the reply
                sender_adress = settings.SITE_MAIL
                receiver_address = parent_reply.author.email
                subject = 'Te han respondido en Social NDW'
                body = render_to_string('sitio/mail_comment_response.html',
                                        {'title': parent_story.title,
                                         'link': parent_story.generate_path()})
                mail.send_mail(sender_adress, receiver_address, subject, body)

        return HttpResponseRedirect(parent_story.generate_path())

    # messages
    else:
        challenge = request.POST.get('recaptcha_challenge_field')
        response  = request.POST.get('recaptcha_response_field')
        remoteip  = environ['REMOTE_ADDR']
        cResponse = captcha.submit(
                         challenge,
                         response,
                         settings.RECAPTCHA_PRIVATEKEY,
                         remoteip)
                         
        
        usr = get_current_user(request)
        use_anonymous = False
        try:
            if usr.invisible_mode:
             use_anonymous = True
        except:
            pass
                    
        key_name = request.POST.get('storyparent', '')
        story = db.get(db.Key(key_name))

        if cResponse.is_valid or usr:
            if ( usr == None or use_anonymous):
                usr = User.objects.get(email=settings.ANONYMOUS_USER_MAIL)

            if title:
                msg = Msg()
                if usr.email == settings.ANONYMOUS_USER_MAIL:
            	    msg.client_ip = '127.0.0.1'
            	    #msg.date = settings.ANONYMOUS_DATETIME 
                else:
                    msg.client_ip = request.META['REMOTE_ADDR']
                msg.storyparent = story
                msg.author = usr
                msg.title = db.Text(request.POST.get('title', ''))
                if msg.title == settings.DEFAULT_COMMENT_TEXT:
                    msg.title = ''
    
                msg.msg_type = request.POST.get('msg_type', 'text')
                save = True
                if msg.msg_type != 'video':
                    save = msg.title
                if save:
                    msg.pop = 0
                    msg.save()
    
                    story.author.pop += 1
                    story.author.save()
                    story.karma += 2
                    story.save()
    
                    if settings.ENABLE_MAIL_ALERTS and story.author.comments_alerts and \
                       not story.author.account_state and story.author.email and \
                       mail.is_email_valid(story.author.email):
                        # send mail alert about the comment
                        sender_adress = settings.SITE_MAIL
                        receiver_address = story.author.email
                        subject = 'Han comentado tu historia'
                        body = render_to_string('sitio/mail_comment_story.html',
                                                {'title': story.title,
                                                 'link': story.generate_path()})
                        mail.send_mail(sender_adress, receiver_address, subject, body)    
            #return HttpResponseRedirect(story.generate_path())
            return HttpResponse(str(msg.id))
        else:
#            return HttpResponseRedirect(story.generate_path() + '?error=1')
            return HttpResponse('0')


@internal_logged_or_fail
def add_message_attach(request):
	msg_key = request.POST.get('msg_id', '')
	msg = db.get(db.Key(msg_key))
	key_name = request.POST.get('storyparent', '')
	story = db.get(db.Key(key_name))
	
	if msg.msg_type == 'video':
	    msg.video = request.POST.get('video', '')
	elif msg.msg_type == 'map':
	    msg.map = request.POST.get('map', '')
	    msg.map_zoom = int(request.POST.get('map_zoom', '1'))
	elif msg.msg_type == 'doc' or msg.msg_type == 'image':
            filekey = None
            try:
                if msg.msg_type == 'doc':
                    uploads = blobstore_helper.get_uploads(request, 'document')
                    filename = request.FILES['document'].name
                else:
                    uploads = blobstore_helper.get_uploads(request, 'image')
                    filename = request.FILES['image'].name
                uploadfile = uploads
                for upload in uploads:
                    filekey = str(upload.id) 
                    if filekey:
                        msg.document = filekey
                        if filename:
                            msg.filename = filename

            except:
                pass
	msg.save()
	return HttpResponseRedirect(story.generate_path())


def popular_users(request):
    '''Popular users ranking.'''
    context = {}

    users = User.all().order_by('-pop')
    add_common_context(request, context)
    context['users'] = users

    return render_to_response('sitio/popular_users.html', context,
                              context_instance=RequestContext(request))

def send_contact_msg(request):
    '''Send contact message.'''
    # FIXME check, is migrated code for POST method
    email = request.POST.get('email', '')
    msg =  request.POST.get('msg', '')
    if email and msg:
        if not mail.is_email_valid(email):
            return HttpResponseRedirect('/contact/?error=2')
        else:
            sender_adress = settings.SITE_MAIL
            stq_address = 'robycibriancampoy@gmail.com'
            subject = 'Contacto'
            body = email + ' escribe:  ' + msg
            mail.send_mail(sender_adress, stq_address, subject, body)
            return HttpResponseRedirect('/contact/?error=0')
    else:
        return HttpResponseRedirect('/contact/?error=1')

def send_recovery_pass(request):
    '''Send recovery pass message.'''
    # FIXME check, is migrated code for POST method
    email = request.POST.get('email', '')
    nickname = request.POST.get('nickname', '')
    if email:
        if not mail.is_email_valid(email):
            return HttpResponseRedirect('/pass_recovery/?error=2')
        else:
            usr = User.objects.filter(nickname=nickname,email=email)[0]
            if usr:
                usr.recovery_key = hashlib.md5(str(random.random())).hexdigest()
                usr.save()
                sender_adress = settings.SITE_MAIL
                receiver_address = usr.email
                subject = 'Tu cuenta de usuario'
                confirmation_url = settings.SITE_BASE_URL + '/pass_recovery?rkey=' + usr.recovery_key
                body = render_to_string('sitio/mail_recover_pass.html',
                                        {'link': confirmation_url})
                mail.send_mail(sender_adress, receiver_address, subject, body)
                return HttpResponseRedirect('/pass_recovery/?error=0')
            else:
                return HttpResponseRedirect('/pass_recovery/?error=2')
    else:
        return HttpResponseRedirect('/pass_recovery/?error=2')

def admin_send_recovery_pass(request, userkey):
    '''Send recovery pass message.'''
    # FIXME check, is migrated code for POST method
    usr = db.get(db.Key(userkey))
    if usr:
        if not mail.is_email_valid(usr.email):
            return HttpResponseRedirect('/admin/users/')
        else:
            usr.recovery_key = hashlib.md5(str(random.random())).hexdigest()
            usr.save()
            sender_adress = settings.SITE_MAIL
            receiver_address = usr.email
            subject = 'Tu cuenta de usuario'
            confirmation_url = settings.SITE_BASE_URL + '/pass_recovery?rkey=' + usr.recovery_key
            body = render_to_string('sitio/mail_recover_pass.html',
                                    {'link': confirmation_url})
            mail.send_mail(sender_adress, receiver_address, subject, body)
            return HttpResponseRedirect('/admin/users/')
    else:
        return HttpResponseRedirect('/admin/users/')



def send_activation_mail(request, user_key):
    '''Send account activation message.'''
    usr = db.get(db.Key(user_key))
    if usr:
        sender_adress = settings.SITE_MAIL
        receiver_address = usr.email
        subject = 'Activa tu cuenta de usuario'
        activation_url = settings.SITE_BASE_URL + '/activate_account/%s/' % usr.activation_key
        body = render_to_string('sitio/mail_activate_account.html',
                                {'link': activation_url})
        mail.send_mail(sender_adress, receiver_address, subject, body)

        return HttpResponseRedirect('/account_message/?message=1') # activation email sended
    else:
        return HttpResponseRedirect('/account_message/?message=4') # activation email not sended

def send_deletion_mail(request, user_key):
    '''Send account deletion message.'''
    usr = db.get(db.Key(user_key))
    if usr:
        usr.deletion_key = hashlib.md5(str(random.random())).hexdigest()
        usr.deletion_msg = request.POST.get('deletion_msg', '')
        usr.save()

        sender_adress = settings.SITE_MAIL
        receiver_address = usr.email
        subject = 'Eliminar cuenta de usuario'
        deletion_url = settings.SITE_BASE_URL + '/delete_account/%s/' % usr.deletion_key
        body = render_to_string('sitio/mail_delete_account.html',
                                {'link': deletion_url})
        mail.send_mail(sender_adress, receiver_address, subject, body)

        return HttpResponseRedirect('/account_message/?message=6') # deletion email sended
    else:
        return HttpResponseRedirect('/account_message/?message=8') # deletion email not sended

def account_message(request):
    '''Account related messages page.'''
    context = {}
    add_common_context(request, context, sidebar_style = SIDEBAR_NOAD)
    context['logout_url'] = '/logout/'  #users.create_logout_url(urlquote('/')) 
    context['message'] = request.GET.get('message', '')
    context['urlback'] = '/'

    return render_to_response('sitio/account_message.html', context,
                              context_instance=RequestContext(request))

def activate_account(request, activation_key):
    '''Do account activation.'''
    usr = User.objects.filter(activation_key=activation_key)[0]
    if usr:
        usr.activation_key = ''
        usr.save()
        request.session['logged_user'] = str(usr.id)

        return HttpResponseRedirect('/account_message/?message=2') # account activated
    else:
        return HttpResponseRedirect('/account_message/?message=3') # account not activated

def delete_account(request, deletion_key):
    '''Do account deletion.'''
    usr = User.objects.filter(deletion_key=deletion_key)[0]
    if usr:
        usr.deletion_key = ''
        usr.account_state = 'deleted'
        usr.save()

        # delete all messages
        msgs = Msg.filter('author =', usr)
        for m in msgs:
            m.status = 1
            m.save()

        # logout
        del request.session['logged_user']

        return HttpResponseRedirect('/account_message/?message=7') # account deleted
    else:
        return HttpResponseRedirect('/account_message/?message=9') # account not deleted

def update_karma(request): 
    '''Send recovery pass message.'''
    # FIXME check, is migrated code
    stories = Story.objects.all().order_by('date')

    for story in stories:
        # FIXME CHECK
        # messages number
        #msgs_str_query = 'SELECT * FROM Msg WHERE storyparent = :1'
        #msgs_query = db.GqlQuery(msgs_str_query, story)
        #try:
        #    msgcount = msgs_query.count()
        #except:
        #    msgcount = 0

        # negative votes number
        #bury_str_query = 'SELECT * FROM Vote WHERE story = :1 AND value = :2'
        #bury_query = db.GqlQuery(bury_str_query, story, 0)
        #burycount = bury_query.count()

        # publication date
        now = datetime.datetime.today()
        tafmsd = datetime.datetime(story.date.year, story.date.month, story.date.day, story.date.hour, story.date.minute, story.date.second)
        difference = now - tafmsd
        #diff = get_formated_time(difference)
        #if diff[1] != '4':
        #    diff[0] = '-1'

        # calc and update karma value
        #karma = (msgcount * 2) + (story.pop * 10) - (burycount * 10)
        #story.karma = karma
        hkarma = story.karma / ( ( ( int( difference.seconds ) / 3600 + 1.99999 ) ) ** 1.5 )
        story.hkarma = hkarma
        story.save()

    context = {}
    context['debug'] = 'ok'
    memcache.flush_all()

    return render_to_response('sitio/debug.html', context,
                              context_instance=RequestContext(request))

@admin_required
def add_category(request):
    '''Add category.'''
    if request.POST.get('title', ''):
        category = Category()
        category.title = request.POST.get('title', '')
        category.name = request.POST.get('name', '')
        category.site = request.session['site']
        category.save()
    return HttpResponseRedirect('/admin/categories/')

@admin_required
def delete_category(request, categorykey):
    '''Delete category.'''
    category = db.get(db.Key(categorykey))
    if category:
        category.delete()
    return HttpResponseRedirect('/admin/categories/')

@admin_required
def edit_category(request, categorykey):
    '''Edit category.'''
    category = db.get(db.Key(categorykey))
    if category:
        if request.method == 'POST':
            category.title = request.POST.get('title', '')
            category.name = request.POST.get('name', '')
            category.site = request.session['site']
            category.save()
        else:
            context = {}
            add_common_context(request, context, sidebar_style = SIDEBAR_NOAD)

            context['category'] = category

            return render_to_response('sitio/edit_category.html', context,
                                      context_instance=RequestContext(request))

    return HttpResponseRedirect('/admin/categories/')

@admin_required
def add_site(request):
    '''Add site.'''
    if request.POST.get('title', ''):
        site = Site()
        site.title = request.POST.get('title', '')
        site.domain = request.POST.get('domain', '')
        site.save()
    return HttpResponseRedirect('/admin/sites/')

@admin_required
def delete_site(request, sitekey):
    '''Delete site.'''
    site = db.get(db.Key(sitekey))
    if site:
        site.delete()
    return HttpResponseRedirect('/admin/sites/')

@admin_required
def edit_site(request, sitekey):
    '''Edit site.'''
    site = db.get(db.Key(sitekey))
    if site:
        if request.method == 'POST':
            site.title = request.POST.get('title', '')
            site.domain = request.POST.get('domain', '')
            site.save()
        else:
            context = {}
            add_common_context(request, context, sidebar_style = SIDEBAR_NOAD)

            context['site'] = site

            return render_to_response('sitio/edit_site.html', context,
                                      context_instance=RequestContext(request))

    return HttpResponseRedirect('/admin/sites/')


@admin_required
def reset_account(request, userkey):
    '''Reset account.'''
    user = db.get(db.Key(userkey))
    if user:
        user.avatar = None
        user.avatar_big = None
        user.avatar_mini = None
        user.avatar_med = None
        user.background = None
        user.name = ''
        user.bio = ''
        user.url = ''
        user.location = ''
        user.comments_alerts = True
        user.replies_alerts = True
        user.save()

    return HttpResponseRedirect('/admin/users/')

@admin_required
def admin_edit_profile(request, userkey):
    '''Edit profile.'''
    user = db.get(db.Key(userkey))
    if user:
        if request.method == 'POST':
            if 'img' in request.FILES:
                try:
                    image = request.FILES['img'].read()
                    user.avatar = db.Blob(images.resize(image, 49, 49))
                    user.avatar_big = db.Blob(image)
                    user.avatar_mini = db.Blob(images.resize(image, 16, 16))
                    user.avatar_med = db.Blob(images.resize(image, 128, 128))
                except:
                    return HttpResponseRedirect('/admin/users/') # image error, possibly a too big file
            if 'imgbg' in request.FILES:
                try:
                    user.background = db.Blob(request.FILES['imgbg'].read())
                except:
                    return HttpResponseRedirect('/admin/users/') # image error, possibly a too big file
            user.name = request.POST.get('name', '')
            user.bio = request.POST.get('bio', '')
            user.url = request.POST.get('url', '')
            if user.url and not user.url.strip().startswith('http'):
                user.url = 'http://' + user.url.strip()
            user.location = request.POST.get('location', '')
            user.comments_alerts = 'comments_alerts' in request.POST
            user.replies_alerts = 'replies_alerts' in request.POST
            user.save()
        else:
            context = {}
            add_common_context(request, context, sidebar_style = SIDEBAR_NOAD)

            context['user_edit'] = user

            return render_to_response('sitio/admin_edit_profile.html', context,
                                      context_instance=RequestContext(request))

    return HttpResponseRedirect('/admin/users/')

@internal_login_required
def user_img(request, user_key, img_type = ''):
    '''Get formated user image.'''
    usr = db.get(db.Key(user_key))
    image_data = None
    if img_type == '':
        if usr.avatar:
            image_data = usr.avatar
        else:
            return HttpResponseRedirect('/static/img/det/avatar.png')
    elif img_type == 'avatar_mini':
        if usr.avatar_mini:
            image_data = usr.avatar_mini
        else:
            return HttpResponseRedirect('/static/img/det/avatar_mini.png')
    elif img_type == 'avatar_big':
        if usr.avatar_big:
            image_data = usr.avatar_big
        else:
            return HttpResponseRedirect('/static/img/det/avatar_big.png')
    elif img_type == 'avatar_med':
        if usr.avatar_med:
            image_data = usr.avatar_med
        else:
            return HttpResponseRedirect('/static/img/det/avatar.png')
    elif img_type == 'background':
        if usr.background:
            image_data = usr.background
        else:
            return HttpResponseRedirect('/static/img/bg-body.png')
    elif img_type == 'banner':
        if usr.banner:
            image_data = usr.banner
        else:
            return HttpResponseRedirect('/static/img/det/avatar.png')
    return HttpResponse(image_data, 'image/png')

@internal_login_required
def story_img(request, story_key):
    '''Get formated story image.'''
    story = db.get(db.Key(story_key))
    if story.avatar:
        image_data = story.avatar
    else:
        image_data = story.image
    return HttpResponse(image_data, 'image/png')
	
@internal_login_required
def story_original_img(request, story_key):
    '''Get formated story image.'''
    story = db.get(db.Key(story_key))
    if story.image:
        image_data = story.image
    else:
        image_data = story.avatar
    return HttpResponse(image_data, 'image/png')

@internal_login_required
def msg_img(request, msg_key):
    '''Get formated comment image.'''
    blob = blobstore.BlobInfo.get(blobstore.BlobKey(msg_key))
    return blobstore_helper.send_blob(request, blob)

@internal_login_required
def msg_img_old(request, msg_key):
    '''Get formated comment image. Old version compatibility.'''
    msg = db.get(db.Key(msg_key))
    image_data = msg.image
    return HttpResponse(image_data, 'image/png')

@internal_login_required
def msg_doc(request, msg_key):
    '''Get formated comment file.'''
    blob = blobstore.BlobInfo.get(blobstore.BlobKey(msg_key))
    return blobstore_helper.send_blob(request, blob, save_as=True)

# AJAX views:

@login_required
def add_friend(request):
    '''Add a friend.'''
    friend_key = str(simplejson.loads(request.GET.get('friendkey', '')))
    user_key = str(simplejson.loads(request.GET.get('userkey', '')))

    friend = db.get(db.Key(friend_key))
    user = db.get(db.Key(user_key))

    relationship = Relationship()
    relationship.user = user
    relationship.friend = friend
    relationship.save()

    if settings.ENABLE_MAIL_ALERTS and \
       not friend.account_state and \
       friend.email and mail.is_email_valid(friend.email):
        # send mail alert about the friendship
        sender_adress = settings.SITE_MAIL
        receiver_address = friend.email
        subject = 'Tienes un nuevo seguidor'
        body = render_to_string('sitio/mail_new_follower.html',
                                {'follower_nickname': user.nickname,
                                 'follower_name': user.name})
        mail.send_mail(sender_adress, receiver_address, subject, body)

    return HttpResponse(simplejson.dumps(1))

@login_required
def remove_friend(request):
    '''Remove a friend.'''
    friend_key = str(simplejson.loads(request.GET.get('friendkey', '')))
    user_key = str(simplejson.loads(request.GET.get('userkey', '')))

    friend = db.get(db.Key(friend_key))
    user = db.get(db.Key(user_key))

    relationship_query = Relationship.objects.get(user=user,friend=friend)
    relationship.delete()

    return HttpResponse(simplejson.dumps(1))


@internal_login_required
def invalid_story(request):
    '''Invalid story messages page.'''
    context = {}
    add_common_context(request, context, sidebar_style = SIDEBAR_NOAD)

    context['urlback'] = '/'

    return render_to_response('sitio/invalid_story.html', context,
                              context_instance=RequestContext(request))

@internal_login_required
def story_followers(request):
    '''Get followers of a story.'''
    story_key = str(simplejson.loads(request.GET.get('storykey', '')))

    story = Story.objects.get(id=story_key)

    votes = Vote.objects.filter(story=story,value=1)

    result = render_to_string('sitio/story_followers.html', {'votes': votes,},
                              context_instance=RequestContext(request))
    return HttpResponse(simplejson.dumps(result))

@internal_login_required
def story_print_options(request):
    '''Get print options for a story.'''
    story_key = str(simplejson.loads(request.GET.get('storykey', '')))

    story = db.get(db.Key(story_key))

    result = render_to_string('sitio/story_print_options.html', {'story': story,},
                              context_instance=RequestContext(request))
    return HttpResponse(simplejson.dumps(result))

@internal_login_required
def more_story_messages(request):
    '''Get more messages of a story.'''
    story_key = str(simplejson.loads(request.GET.get('storykey', '')))
    page = int(str(simplejson.loads(request.GET.get('page', ''))))
    chtml = ''

    story = db.get(db.Key(story_key))

    usr = get_current_user(request)

    allow_comments = True
    try:
        if story.block_anonymous:
            if not usr or usr.invisible_mode:
                allow_comments = False
    except:
        pass

    if not usr or usr.invisible_mode:
        allow_comments = False

    context = {}
    context['allow_comments'] = allow_comments
    msgs = messages_paginated(story, page, context)
    if usr:
	   is_anon = '1'
	   context['is_anon'] = '1'
    else:
        is_anon = '0'
        context['is_anon'] = '0'
        chtml = captcha.displayhtml(
        public_key = settings.RECAPTCHA_KEY,
          use_ssl = False,
          error = None)
    context['captchahtml'] = chtml
    result = render_to_string('sitio/story_messages.html',
                              {'story': story,
                               'msgs': msgs,
                               'more_msgs_link': len(msgs) == MESSAGES_ON_PAGE,
                               'user': usr,
                               'is_anon': is_anon,
                               'captchahtml': chtml,
                               'page': page + 1,
                               'default_comment_text': settings.DEFAULT_COMMENT_TEXT,
                               'allow_comments': allow_comments},
                              context_instance=RequestContext(request))
    return HttpResponse(simplejson.dumps(result))

@login_required
def delete_avatar(request):
    '''Delete user's avatar.'''
    user_key = str(simplejson.loads(request.GET.get('userkey', '')))

    user = db.get(db.Key(user_key))
    user.avatar_big = None
    user.avatar = None
    user.avatar_med = None
    user.avatar_mini = None
    user.save()
    return HttpResponse(simplejson.dumps(1))

@login_required
def delete_bg(request):
    '''Delete user's background.'''
    user_key = str(simplejson.loads(request.GET.get('userkey', '')))

    user = db.get(db.Key(user_key))
    user.background = None
    user.save()
    return HttpResponse(simplejson.dumps(1))

@login_required
def delete_message(request):
    '''Delete message.'''
    msg_key = str(simplejson.loads(request.GET.get('msgkey', '')))


    msg = db.get(db.Key(msg_key))
    msg.status = 1
    msg.save()

    return HttpResponse(simplejson.dumps(str(msg.id)))

@login_required
def delete_reply(request):
    '''Delete reply.'''
    reply_key = str(simplejson.loads(request.GET.get('replykey', '')))

    reply = db.get(db.Key(reply_key))
    reply.status = 1
    reply.save()

    return HttpResponse(simplejson.dumps(str(reply.id)))

@login_required
def vote_msg(request):
    '''Vote message.'''
    msg_key = str(simplejson.loads(request.GET.get('msgkey', '')))
    vote_type = str(simplejson.loads(request.GET.get('votetype', '')))

    msg = db.get(db.Key(msg_key))
    user = get_current_user(request)

    vote = Vote.objects.get(author=user,msg=msg)

    if not vote:
        vote = Vote()
        vote.msg = msg
        vote.author = user
        vote.value = 0

    if vote_type == 'add':
        if vote.value < 1:
            vote.value += 1
            vote.save()
            msg.pop += 1
            msg.save()
            msg.author.pop += 1
            msg.author.save()
    elif vote_type == 'remove':
        if vote.value > -1:
            vote.value -= 1
            vote.save()
            msg.pop -= 1
            msg.save()
            msg.author.pop -= 1
            msg.author.save()

    return HttpResponse(simplejson.dumps(str(msg.id) + " " + str(msg.pop)))

@login_required
def vote_reply(request):
    '''Vote reply.'''
    reply_key = str(simplejson.loads(request.GET.get('replykey', '')))
    vote_type = str(simplejson.loads(request.GET.get('votetype', '')))

    reply = Reply.objects.get(id=reply_key)
    user = get_current_user(request)

    vote = Vote.objects.get(author=1,reply=reply)

    if not vote:
        vote = Vote()
        vote.reply = reply
        vote.author = user
        vote.value = 0

    if vote_type == 'add':
        if vote.value < 1:
            vote.value += 1
            vote.save()
            reply.pop += 1
            reply.save()
            reply.author.pop += 1
            reply.author.save()
    elif vote_type == 'remove':
        if vote.value > -1:
            vote.value -= 1
            vote.save()
            reply.pop -= 1
            reply.save()
            reply.author.pop -= 1
            reply.author.save()

    return HttpResponse(simplejson.dumps(str(reply.id) + " " + str(reply.pop)))

@login_required
def vote_story(request):
    '''Vote story.'''
    story_key = str(simplejson.loads(request.GET.get('storykey', '')))
    vote_type = str(simplejson.loads(request.GET.get('votetype', '')))

    story = Story.objects.get(id=story_key)
    user = get_current_user(request)

    vote = Vote.objects.get(author=user,story=story)

    if not vote:
        vote = Vote()
        vote.story = story
        vote.author = user
        vote.value = 0

    if vote_type == 'add':
        if vote.value < 1:
            vote.value += 1
            vote.save()
            # karma
            story.karma += 10
            story.pop += 1
            story.save()
            story.author.pop += 1
            story.author.save()
    elif vote_type == 'remove':
        if vote.value > -1:
            vote.value -= 1
            vote.save()
            story.karma -= 10
            story.save()
            story.author.pop -= 1
            story.author.save()

    return HttpResponse(simplejson.dumps(str(story.id) + " " + str(story.pop) + " " + vote_type))
	


##### utils / indev #####


### OAuth access ###

def get_access_token(request):
    saved_request_token = gdata.gauth.AeLoad('myKey')
    urlpath = request.path + "?oauth_verifier=" + request.GET.get('oauth_verifier', '') + "&oauth_token=" + request.GET.get('oauth_token', '')
    request_token = gdata.gauth.AuthorizeRequestToken(saved_request_token, urlpath)

    client = gdata.docs.client.DocsClient(source='ndw-social-v1')
    access_token = client.GetAccessToken(request_token)
    client.auth_token = access_token

    user = oauth.get_current_user()
    return HttpResponse(user)

    #feed = client.GetDocList()
    #user = oauth.get_current_user()
    #return HttpResponse(feed)
    #return HttpResponseRedirect('/')
    
   

@login_required
def get_story_from_x(request):
    '''Get story from external source'''
    # cargar url
    feed = request.GET.get('feed')
    result = urlfetch.fetch(feed)
    context = {}

    user = get_current_user(request) 
    if user:
	    context['is_anon'] = '0'
    else:
        context['is_anon'] = '1'
        chtml = captcha.displayhtml(
        public_key = settings.RECAPTCHA_KEY,
          use_ssl = False,
          error = None)

    #return HttpResponse(simplejson.dumps( 'ok1,ok2'))
    if result.status_code == 200:
        ibuffer = result.content  

        #buscar subject
        ctitle = ''
        marker_pos = ibuffer.find("Viewing cable") + 14
        str_closetabletag_pos = ibuffer.find('h3', marker_pos) - 2
        if marker_pos > 0 and str_closetabletag_pos > 0:
             ctitle = ibuffer[marker_pos:str_closetabletag_pos ]
    
        #buscar summary
        csummary = ''
        marker_pos2 = ibuffer.find('#par1', marker_pos) + 13
        str_closetabletag_pos = ibuffer.find('#par2', marker_pos2) - 24
        if marker_pos2 > 0 and str_closetabletag_pos > 0:
             csummary = ibuffer[marker_pos2:str_closetabletag_pos]
    
        categories = Category.objects.filter(site=request.session['site']).order_by('name')

        context['ctitle'] = ctitle
        context['categories'] = categories
        context['csummary'] = csummary.replace('&#x000A;', ' ').replace('&#x', ' ')
        context['url'] = request.GET.get('feed')
         
        #devuelve el formulario de carga
        resultr = render_to_string('sitio/new_story_from_x.html', context,
                            context_instance=RequestContext(request))
        return HttpResponse(resultr)
    else:
        return HttpResponse(simplejson.dumps( '0' ))

@login_required
def get_stories_from_x(request):
    '''Get stories from external source'''

    # cargar url
    url = request.GET.get('feed')
    context = {}
    context['get_feed'] = url
    result = urlfetch.fetch(url)
    if result.status_code == 200:
        ibuffer = result.content  

    #buscar inicio y fin de la tabla
    marker_pos = ibuffer.find("<table", ibuffer.find("pane big"))
    str_closetabletag_pos = ibuffer.find('</table>', marker_pos)
    if marker_pos > 0 and str_closetabletag_pos > 0:
         str_subbuffer = ibuffer[marker_pos:str_closetabletag_pos]
         href_is_valid = True
         str_values = ''
         ipos = 0
         
         # buscar urls
         while href_is_valid:
               str_opentag_pos = str_subbuffer.find('href=', ipos) + 6
               str_closetag_pos = str_subbuffer.find(".html", str_opentag_pos) + 5
               str_href = str_subbuffer[str_opentag_pos : str_closetag_pos]
               ipos = str_closetag_pos 
               if str_href.find('cable') > 0 and str_href.find('cable') < 10:
                   str_values += "http://www.wikileaks.ch" + str_href + ","
               if str_subbuffer.find('href=', ipos) < 0:
                   href_is_valid = False
         urls = str_values.split(',')
         context['urls'] = urls
         context['urls_count'] = len(urls)
         
         #devuelve el formulario de carga
         resultr = render_to_string('sitio/new_story_from_x.html', context,
                              context_instance=RequestContext(request))
         return HttpResponse(resultr)
    else:
         return HttpResponse(simplejson.dumps('error 1'))
    return HttpResponse(simplejson.dumps('error 2'))

@login_required
@admin_required
def get_stories_from_feed(request):
    '''Get stories from feed'''
    feed = str(simplejson.loads(request.GET.get('feed', '')))
    buffer = urllib.urlopen(feed).read()
    if buffer:
         return HttpResponse(simplejson.dumps( buffer ))
    else:
	     return 2


@login_required
@admin_required
def add_stories_from_feed(request):
    '''Add stories in bulk, from feed'''
    # FIXME
    for i in range( int( request.POST.get('items-count') ) ):
        title = request.POST.get('title_' + str(i))
        description = request.POST.get('description_' + str(i))
        category = request.POST.get('category_' + str(i))
        link = request.POST.get('link_' + str(i))
        # story
        story = None
        if title and description and category:
            story = Story()
            story.client_ip = request.META['REMOTE_ADDR']
		
            story.link = link
            if ( story.link ):
                 exist_prev_query = Story.objects.get(link=story.link)
                 exist_prev_count = exist_prev_query.count()
                 if exist_prev_count:
                     prev_story = exist_prev_query.get()
                     return HttpResponseRedirect( prev_story.generate_path() + '?msg=1' ) # exist prev history, same title		

            usr = get_current_user(request)

            use_anonymous = False
            if ( usr == None ):
                use_anonymous = True
            else:
                try:
                    if usr.invisible_mode:
                        use_anonymous = True
                except:
                    pass

            if use_anonymous:
                usr = User.objects.get(email=ANONYMOUS_USER_MAIL)

            story.author = usr
            story.url = urlquote(title.replace('/', '-').replace(' ', '-').lower())
            urlprev_query = Story.get(url=story.url)
            urlprev_count = urlprev_query.count()
            if urlprev_count:
                story.save()
                story.url = story.url + '-' + str(story.id)
            story.title = title

            story.bio = description
            if story.link and not story.link.strip().startswith('http'):
                story.link = 'http://' + story.link.strip()

            category = Category.objects.filter(name=category)[0]
            story.category = category
            story.pop = 1
            story.karma = 10
            if usr.email == settings.ANONYMOUS_USER_MAIL:
            	story.client_ip = '127.0.0.1'
            	#story.date = settings.ANONYMOUS_DATETIME
            story.save()
            # first vote
            vote = Vote()
            vote.value = 1
            vote.story = story
            vote.author = usr
            vote.save()

    return HttpResponseRedirect('/')


@login_required
@admin_required
def update_tasks(request):
    try:
        for s in Story.all():
            s.status = 0
            s.save()
            if s.pop == None:
                s.pop = 0
                s.save()

        for m in Msg.all():
            if m.status == None:
                m.status = 0
                m.save()
            if m.pop == None:
                m.pop = 0
                m.save()

        for r in Reply.all():
            if r.status == None:
                r.status = 0
                r.save()
            if r.pop == None:
                r.pop = 0
                r.save()

        for u in User.all():
            if u.pop == None:
                u.pop = 0
            u.save()

        return HttpResponse('ok')
    except Exception, e:
        return HttpResponse(str(e))


def cache_flush(request):
    memcache.flush_all()
    return HttpResponse('Cache updated.')

def delete_spam(request):
    q = Msg.objects.filter(client_ip='').delete()
    return HttpResponse('Ok.')
   
