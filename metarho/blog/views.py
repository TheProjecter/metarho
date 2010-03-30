import datetime
import time

from django.http import Http404

from metarho.blog.decorators import wp_post_redirect
from metarho import render_with_context
from metarho.blog.models import Post

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