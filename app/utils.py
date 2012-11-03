import urllib
import datetime

from django.utils.http import urlquote
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from app.models import User, Site

def login_required(f):
    '''Custom login required decorator, only on internal site.'''
    def wrap(request, *args, **kwargs):
        user = get_current_user(request)
        if not user:
            return HttpResponseRedirect("/login/")
        else:
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


