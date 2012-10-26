from django.conf.urls import patterns, include, url
import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

#from sitio.feed import AllStories, StoriesByCategory, StoriesByUser

#feeds = {
#    'stories': AllStories,
#    'categories': StoriesByCategory,
#    'users': StoriesByUser,
#}

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^static/(.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_URL})
)

urlpatterns += patterns('app.views',
    (r'^$','index'),
    (r'^legal/$', 'legal'),
    (r'^get_access_token/$', 'get_access_token'),
    (r'^contact/$', 'contact'),
    (r'^search/$', 'search'),
    (r'^cache_flush/$', 'cache_flush'),
    (r'^new_story/$', 'new_story'),
    (r'^new_story$', 'new_story'), 
    (r'^login/$', 'login'),
    (r'^signup/$', 'signup'),
    (r'^edit_profile/$', 'edit_profile'),
    (r'^view_profile/(.*)/$', 'view_profile'),
    (r'^pass_recovery/$', 'pass_recovery'), 
    (r'^pass_recovery$', 'pass_recovery'),
    (r'^add_user/$', 'add_user'), 
    (r'^do_login/$', 'do_login'), 
    (r'^logout/$', 'logout'),
    (r'^save_profile/$', 'save_profile'),
    (r'^save_pass/$', 'save_pass'),
    (r'^add_story/$', 'add_story'),
    (r'^delete_story/(.*)/$', 'delete_story'),
    (r'^add_stories_from_feed/$', 'add_stories_from_feed'), 
    (r'^add_message/$', 'add_message'), 
    (r'^send_contact_msg/$', 'send_contact_msg'), 
    (r'^send_recovery_pass/$', 'send_recovery_pass'), 
    (r'^send_activation_mail/(.*)/$', 'send_activation_mail'),
    (r'^send_deletion_mail/(.*)/$', 'send_deletion_mail'),
    (r'^activate_account/(.*)/$', 'activate_account'),
    (r'^delete_account/(.*)/$', 'delete_account'),
    (r'^account_message/$', 'account_message'),
    (r'^story_img/(.*)/$', 'story_img'),
    (r'^story_original_img/(.*)/$', 'story_original_img'), 
    (r'^msg_img/(.*)/$', 'msg_img'),
    (r'^msg_original_img/(.*)/$', 'msg_img'),
    (r'^msg_original_img_old/(.*)/$', 'msg_img_old'),
    (r'^user_img/(.*)/(.*)/$', 'user_img'),
    (r'^user_img/(.*)/$', 'user_img'),
    (r'^update_karma/$', 'update_karma'), 
    (r'^ajax/add_friend/$', 'add_friend'),
    (r'^ajax/remove_friend/$', 'remove_friend'),
    #(r'^ajax/story_wall/$', 'story_wall'),
    (r'^ajax/story_followers/$', 'story_followers'),
    (r'^ajax/more_story_messages/$', 'more_story_messages'),
    (r'^ajax/delete_avatar/$', 'delete_avatar'),
    (r'^ajax/delete_bg/$', 'delete_bg'),
    (r'^ajax/delete_message/$', 'delete_message'),
    (r'^ajax/delete_reply/$', 'delete_reply'),
    (r'^ajax/vote_msg/$', 'vote_msg'),
    (r'^ajax/vote_reply/$', 'vote_reply'), 
    (r'^ajax/vote_story/$', 'vote_story'), 
    (r'^print_story/(.*)/$', 'print_story'),
    (r'^popular_users/$', 'popular_users'),
    (r'^invalid_story/$', 'invalid_story'),
    ('^(.*)/(.*)/', 'story'), # category/story
    ('^(.*)/', 'index'), # category
	('^(.*)', 'view_profile'), # user profile
)