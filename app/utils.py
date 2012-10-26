import urllib
import datetime

#from google.appengine.ext import db

from django.utils.http import urlquote
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
#from google.appengine.api import users
from app.models import User, Site

def login_required(f):
    '''Custom login required decorator, only on internal site.'''
    def wrap(request, *args, **kwargs):
        if (settings.SITE_MODE == settings.SITE_MODE_INTERNAL) and 'logged_user' not in request.session:
            user = users.get_current_user()
            if not user:
            	return HttpResponseRedirect(users.create_login_url(urlquote(request.path)))
            else:
                 domain = user.email()[user.email().find('@') + 1 : len(user.email())] 
                 site = Site().all().filter('domain =', domain).get()
                 if site != 'None':
                 	request.session['site'] = site
            user_query = db.GqlQuery('SELECT * FROM User WHERE email = :1', user.email())
            usr = user_query.get()
            if usr:
                 if request.session['site']:
	                 request.session['logged_user'] = str(usr.key())
	                 return HttpResponseRedirect(urlquote(request.path))
                 else:
                     return HttpResponseRedirect('/account_message/?message=12&username=' + user.email() + '&domain=' + domain)
            else:
                 if request.session['site']:
                     usr = User()
                     usr.email = user.email()
                     usr.nickname = user.email()[0 : user.email().find('@') ] 
                     usr.googleuser = user
                     usr.is_admin = False
                     usr.comments_alerts = True
                     usr.replies_alerts = True
                     usr.pop = 0
                     usr.activation_key = ''
                     usr.put()
                     request.session['logged_user'] = str(usr.key())
                     return HttpResponseRedirect('/account_message/?message=2')
                 else:
                     return HttpResponseRedirect('/account_message/?message=12&v=1&username=' + user.email() + '&domain=' + domain)

        else:
            return f(request, *args, **kwargs)
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap


# TODO
def internal_login_required(f):
    '''Custom login required decorator, only on internal site.'''
    def wrap(request, *args, **kwargs):
        return f(request, *args, **kwargs)
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap

def logged_or_fail(f):
    '''Logged-only views decorator.'''
    def wrap(request, *args, **kwargs):
        if 'logged_user' not in request.session:
            return HttpResponseRedirect('/')
        else:
            return f(request, *args, **kwargs)
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap

# TODO
def internal_logged_or_fail(f):
    '''Logged-only views decorator, only on internal site.'''
    def wrap(request, *args, **kwargs):
        return f(request, *args, **kwargs)
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap

def admin_required(f):
    '''Admin-only views decorator.'''
    def wrap(request, *args, **kwargs):
        if 'logged_user' in request.session:
            if get_current_user(request).is_admin:
                return f(request, *args, **kwargs)
        return HttpResponseRedirect('/')
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap

def get_current_user(request):
    '''Get logged in user.'''
    if 'logged_user' in request.session:
        key_name = request.session['logged_user']
        usr = User.objects.get(id=key_name)
        if usr:
            return usr
        else:
            return None

def get_formated_time(difference):
    '''Relative time span.'''
    # instants
    diff = difference.seconds
    difference_unit = '1'
    if difference.days > 0:
        # minutes
        difference_unit = '4'
        diff = difference.days
    elif difference.seconds > 3600:
        # hours
        difference_unit = '3'
        diff = difference.seconds / 3600
    elif difference.seconds > 60:
        # days
        difference_unit = '2'
        diff = difference.seconds / 60
    return_value = []
    return_value.append(diff)
    return_value.append(difference_unit)
    return return_value

def custom_settings_context(request):
    '''Context processor for custom settings.'''
    from django.conf import settings
    return {'gmaps_api_key': settings.GMAPS_API_KEY,
            'fb_api_key': settings.FACEBOOK_API_KEY,
            'tw_api_user': settings.TWITTER_API_USER,
            'tw_api_key': settings.TWITTER_API_KEY,
            'analytics_api_key': settings.ANALYTICS_API_KEY,
            'google_ad_client': settings.GOOGLE_AD_CLIENT,
            'google_ad_slot': settings.GOOGLE_AD_SLOT,
            'internal_mode': settings.SITE_MODE == settings.SITE_MODE_INTERNAL,
            'allowed_user_domains': settings.ALLOWED_USER_DOMAINS,
            'gjs_api_key': settings.GJS_API_KEY}


