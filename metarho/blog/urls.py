from django.conf.urls.defaults import *

urlpatterns = patterns('metarho.blog.views',
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[0-9A-Za-z-]+)/$', 'post_detail', name='post-detail'),  
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$', 'post_day', name='list-day'),  
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$', 'post_month', name='list-month'),  
    url(r'^(?P<year>\d{4})/$', 'post_year', name='list-year'),  
    url(r'^/?$', 'post_all', name='index'),
)