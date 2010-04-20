
from django.http import Http404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from metarho.blog.models import Post

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