# file blog_tags.py
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

# Contains various tags to use related to the blog models and features.
from django import template

from metarho.blog.models import Topic
from metarho.blog.models import Tag
from metarho.blog.models import Post

register = template.Library()

@register.inclusion_tag('blog/snippets/topics_nav.xhtml')
def topic_navlinks():
    '''Returns all published topics.'''
    topics = Topic.objects.published()
    return {'topics': topics}

@register.inclusion_tag('blog/snippets/topics_block.xhtml')
def topic_block():
    '''Returns a menu of published topics.'''
    topics = Topic.objects.published()
    return {'topics': topics}

@register.inclusion_tag('blog/snippets/tag_cloud.xhtml')
def tag_cloud_block():
    '''Renders a tag cloud for tags with published posts.'''
    tags = Tag.objects.published()
    return {'tags': tags}

@register.inclusion_tag('blog/snippets/month_archive_block.xhtml')
def archive_list():
    '''Produces a list of months with published posts in them.'''
    dates = Post.objects.published().order_by('pub_date').dates('pub_date', 'month')
    return {'dates': dates}