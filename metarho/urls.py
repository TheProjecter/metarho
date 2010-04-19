from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'metarho.blog.views.post_all', name='site-index'),
    (r'^admin/', include(admin.site.urls)),
    (r'^', include("metarho.blog.urls", namespace="blog"))
)

# DISABLE THIS IN PRODUCTION
if settings.DEV_ENV:
    from os import path
    urlpatterns += patterns('',
        (r'^sitemedia/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': path.join(settings.BASE_DIR, '../media')
            }),
    )
