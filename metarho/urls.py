# file urls.py
#
# Copyright 2010 Scott Turnbull
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'metarho.blog.views.post_all', name='site-index'),
    (r'^admin/', include(admin.site.urls)),
    #(r'tag/', include("metarho.ontology.tag_urls", namespace="tag")),
    #(r'topic/', include("metarho.ontology.topic_urls", namespace="topic")),
    (r'^', include("metarho.blog.urls", namespace="blog")),
)

# DISABLE THIS IN PRODUCTION
if settings.DEV_ENV:
    from os import path
    urlpatterns += patterns('',
        (r'^sitemedia/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': path.join(settings.BASE_DIR, '../media')
            }),
    )
