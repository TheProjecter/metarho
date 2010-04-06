import datetime
import time

from django.http import Http404
from django.shortcuts import get_object_or_404

from metarho.blog.decorators import wp_post_redirect
from metarho import render_with_context
from metarho.blog.models import Post
from metarho.blog.models import Tag
from metarho.blog.models import Topic

# All Posts List Methods.
@wp_post_redirect
def post_all(request):
    '''Returns all User Blogs'''
    posts = Post.objects.published()
    
    return render_with_context(request, 'blog/post_list.xhtml', {
            'title': 'All Posts',                                                
            'posts': posts,
            })
    
def post_year(request, year):
    '''Returns all posts for a particular year.'''
    tt = time.strptime('-'.join([year]), '%Y')
    date = datetime.date(*tt[:3])
    posts = Post.objects.published().filter(pub_date__year=date.year)
    
    return render_with_context(request, 'blog/post_list.xhtml', {
            'posts': posts,
            'title': 'Posts for %s' % date.strftime("%Y"),                                     
            })

def post_month(request, year, month):
    '''Returns all posts for a particular month.'''
    tt = time.strptime('-'.join([year, month]), '%Y-%b')
    date = datetime.date(*tt[:3])
    posts = Post.objects.published().filter(pub_date__year=date.year, 
                            pub_date__month=date.month)
    
    return render_with_context(request, 'blog/post_list.xhtml', {
            'posts': posts,
            'title': 'Posts for %s' % date.strftime("%B %Y"),                                     
            })

def post_day(request, year, month, day):
    '''Returns all posts for a particular day.'''
    tt = time.strptime('-'.join([year, month, day]), '%Y-%b-%d')
    date = datetime.date(*tt[:3])
    posts = Post.objects.published().filter(pub_date__year=date.year, 
                            pub_date__month=date.month, pub_date__day=date.day)
    
    return render_with_context(request, 'blog/post_list.xhtml', {
            'posts': posts,
            'title': 'Posts for %s' % date.strftime("%A, %d %B %Y"),                                     
            })

# Detail Views
def post_detail(request, year, month, day, slug):
    ''' Returns an individual post.'''
    tt = time.strptime('-'.join([year, month, day]), '%Y-%b-%d')
    date = datetime.date(*tt[:3])
    try:
        post = Post.objects.published().get(slug=slug, pub_date__year=date.year, 
                            pub_date__month=date.month, pub_date__day=date.day)
    except Post.DoesNotExist:
        raise Http404
    
    return render_with_context(request, 'blog/post_detail.xhtml', {
            'post': post,
            'title': post.title,                                     
            })

# Topics and Tags Views
def post_topic(request, slug):
    '''Returns all posts related to a topic.'''
    topic = get_object_or_404(Topic, slug=slug)
    posts = Post.objects.published().filter(topics=topic)

    return render_with_context(request, 'blog/post_list.xhtml', {
                'posts': posts,
                'title': topic.text,
            })

def post_tag(request, slug):
    '''Returns all posts related to tags.'''
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.published().filter(tags=tag)

    return render_with_context(request, 'blog/post_list.xhtml', {
            'posts': posts,
            'title': 'Posts under tag "%s"' % tag.text,
            })
def tag_list(request):
    '''Displays all tags for posts.'''

    tags = Tag.objects.published()

    return render_with_context(request, 'blog/tag_list.xhtml', {
            'tags': tags,
            'title': 'Viewing Tags',
           })

def topic_list(request):
    '''Displays a list of topics.'''

    topics = Topic.objects.published()

    return render_with_context(request, 'blog/topic_list.xhtml', {
                'topics': topics,
                'title': 'Topics'
            })

# Topics and Tags list views
def post_topic_year(request, slug, year):
    '''Returns all posts under a topic for a particular year.'''
    topic = get_object_or_404(Topic, slug=slug)
    tt = time.strptime('-'.join([year]), '%Y')
    date = datetime.date(*tt[:3])
    posts = Post.objects.published().filter(pub_date__year=date.year, topics=topic)

    return render_with_context(request, 'blog/post_list.xhtml', {
            'posts': posts,
            'title': 'Posts under %s for %s' % (topic.text , date.strftime("%Y")),
            })

def post_topic_month(request, slug, year, month):
    '''Returns all posts for a particular month.'''
    topic = get_object_or_404(Topic, slug=slug)
    tt = time.strptime('-'.join([year, month]), '%Y-%b')
    date = datetime.date(*tt[:3])
    posts = Post.objects.published().filter(pub_date__year=date.year,
                            pub_date__month=date.month, topics=topic)

    return render_with_context(request, 'blog/post_list.xhtml', {
            'posts': posts,
            'title': 'Posts under %s for %s' % (topic.text, date.strftime("%B %Y")),
            })

def post_topic_day(request, slug, year, month, day):
    '''Returns all posts for a particular day.'''
    topic = get_object_or_404(Topic, slug=slug)
    tt = time.strptime('-'.join([year, month, day]), '%Y-%b-%d')
    date = datetime.date(*tt[:3])
    posts = Post.objects.published().filter(pub_date__year=date.year, topics=topic, 
                            pub_date__month=date.month, pub_date__day=date.day)

    return render_with_context(request, 'blog/post_list.xhtml', {
            'posts': posts,
            'title': 'Posts under %s for %s' % (topic.text, date.strftime("%A, %d %B %Y")),
            })