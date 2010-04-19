
from django.http import Http404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from metarho.blog.models import Post

CONTENT_MAP = {
    'application/json': ('metarho.blog.json', '_json'),
    'text/xml': ('metarho.blog.feeds', '_rss'),
    'application/rss+xml': ('metarho.blog.feeds', '_rss'),
    'application/atom+xml': ('metarho.blog.feeds','_atom'),
    'application/rdf+xml': ('metarho.blog.rdf', '_rdf')
}

FORMAT_MAP = {
    'html': 'text/html',
    'json': 'application/json',
    'xml': 'text/xml',
    'rss': 'application/rss+xml',
    'atom': 'application/atom+xml',
    'rdf': 'application/rdf+xml',
}

def format_req(fmt, new_fn):
    '''

    for example if there the decorated view method was called 'post_list'
    and the format attribue of the querystring was rss::

       /posts/?format=rss

    Then it would match a value in the FORMAT_MAP and return the method
    'metarho.blog.feeds.post_list_rss instead.

    '''

    def _decorator(view_fn):
        def _wraped(request, *args, **kwargs):
            req_format = request.GET.get('format', None)
            if req_format == fmt:
                return new_fn(request, *args, **kwargs)
            # Default to returning the original method
            return view_fn(request, *args, **kwargs)
        return _wraped 
    return _decorator

def wp_post_redirect(view_fn):
    '''
    Checks a request for a querystring item matching a wordpress 
    post request.
    
    This is to enables url redirects for blog migrations from wordrpess.
    To use just decorate the view method for your default blog location.
    
    '''
    def decorator(request, *args, **kwargs):
        wp_query = request.GET.get('p', None)
        if wp_query:
            try:
                post = Post.objects.published().get(postmeta__key='wp_post_id', 
                                                    postmeta__value=wp_query)
                ar = post.pub_date.strftime("%Y/%b/%d").split('/')
                ar.append(post.slug)
                htr = HttpResponseRedirect(reverse('blog:post-detail', args=ar))
                htr.status_code = 301 # This should reflect a 'Moved Permanently' code.
                return htr
            except Post.DoesNotExist:
                raise Http404
        return view_fn(request, *args, **kwargs)
    
    return decorator