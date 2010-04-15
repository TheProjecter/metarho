# Admin classes for tracback models
from django.contrib import admin
from metarho.blog.models import Post
from metarho.blog.models import Topic
from metarho.blog.models import Tag
from metarho.blog.models import PostMeta
from metarho.blog.models import Publication

from django.conf import settings
media = settings.MEDIA_URL

class PostMetaInline(admin.TabularInline):
    model = PostMeta

class PostAdmin(admin.ModelAdmin):
    '''
    Admin interface options for the Post model.
    '''
    search_fields = ['title']
    list_display = ('title', 'status')
    list_filter = ('status', 'pub_date', 'author', 'topics')
    inlines = [PostMetaInline,]
    
    class Media:
        js = (
              'http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js',
              ''.join([media, '/js/ckeditor/ckeditor.js']),
              ''.join([media, '/js/ckeditor/adapters/jquery.js']),
              ''.join([media, '/js/adminpostwysiwyg.js']),
              )
    
class TopicAdmin(admin.ModelAdmin):
    search_fields = ['text']
    
class TagAdmin(admin.ModelAdmin):
    search_fields = ['text']

admin.site.register(Publication)
admin.site.register(Post, PostAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Topic, TopicAdmin)