from django.conf.urls.defaults import *

urlpatterns = patterns('metarho.blog.views',
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[0-9A-Za-z-]+)/$', 'post_detail', name='post-detail'),  
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/$', 'post_day', name='list-day'),  
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/$', 'post_month', name='list-month'),  
    url(r'^(?P<year>\d{4})/$', 'post_year', name='list-year'),
    url(r'^tag/$', 'tag_list', name='tag-list'),
    url(r'^tag/(?P<slug>[\w\-]+)/$', 'post_tag', name='post-tag'),
    url(r'^topic/$', 'topic_list', name='topic-list'),
    url(r'^topic/(?P<path>.*)$', 'post_topic', name='post-topic'),
    url(r'^archive/$', 'archive_list', name='archive-list'),
    url(r'^/?$', 'post_all', name='index'),
    url(r'^atom/$', 'post_all_feed', name="index-feed"),
)