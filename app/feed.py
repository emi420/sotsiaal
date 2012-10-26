from django.contrib.syndication.feeds import Feed
from sitio.models import Category, Story, User
import collections

class BaseFeed(Feed):
    title_template = 'feeds/title.html'
    description_template = 'feeds/description.html'

    def item_link(self, item):
        return item.generate_path()

class AllStories(BaseFeed):
    title = 'Historias en SocialNDWay'
    link = '/'
    description = 'Historias actualmente populares en SocialNDWay'

    def items(self):
        return Story.all().filter('karma >', 0).order('-karma')[:15]

class StoriesByCategory(BaseFeed):
    def get_object(self, bits):
        return Category.all().filter('name =', bits[0]).get()

    def title(self, obj):
        return 'Historias sobre %s en SocialNDWay' % obj.title

    def description(self, obj):
        return 'Historias actualmente populares en SocialNDWay, referidas a %s' % obj.title

    def link(self, obj):
        return '/%s/' % obj.name

    def items(self, obj):
        return Story.all().filter('category =', obj).filter('karma >', 0).order('-karma')[:15]

class StoriesByUser(BaseFeed):
    def get_object(self, bits):
        return User.all().filter('nickname =', bits[0]).get()

    def title(self, obj):
        return 'Historias de %s en SocialNDWay' % obj.nickname

    def description(self, obj):
        return 'Historias en SocialNDWay, publicadas por %s' % obj.nickname

    def link(self, obj):
        return '/view_profile/%s/' % obj.nickname

    def items(self, obj):
        return Story.all().filter('author =', obj).filter('karma >', 0).order('-karma')[:15]

