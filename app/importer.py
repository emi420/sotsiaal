from django.http import HttpResponse
from app.models import Category, Story
from app.utils import *
import feedparser

@login_required
@admin_required
def importer(request):
    # Import data from feed
    # FIXME CHECK
    entries = feedparser.parse(request.GET.get('url', ''))["items"]
    category = request.GET.get('category', '')
    count = 0
    
    for entry in entries:
        prev_story = None
        try:
            # Custom data
            prev_story = Story.objects.filter(title=entry.titulo,bio=entry.descripcion)[0]
        except:
            prev_story = None
            
        if prev_story is None:
    
            story = Story()
            
            # Custom data
            
            story.title = entry.titulo
            story.bio = entry.descripcion
            #story.link = entry.link

            story.author = get_current_user(request)
            story.category = Category.objects.get(name=category)
            story.pop = 0
            story.karma = 0
            story.status = 0
            story.site_id
            story.hkarma = 0
            story.site = Site.objects.get(domain=settings.SITE_DOMAIN)
            story.url = urlquote(story.title.replace('/', '-').replace(' ', '-').lower())
            story.save()
            
            count = count + 1
            
    return HttpResponse(str(count) + ' entries imported.')