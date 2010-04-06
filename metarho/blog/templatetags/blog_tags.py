# Contains various tags to use related to the blog models and features.
from django import template

from metarho.blog.models import Topic
from metarho.blog.models import Tag

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