from metarho import render_with_context
from metarho.blog.models import Post

def post_all(request):
    '''Returns all User Blogs'''
    posts = Post.objects.published()
    
    return render_with_context(request, 'blog/post_list.xhtml', {
            'title': 'Blog Posts',                                                
            'posts': posts,
            })
    
def post_year(request, year):
    pass

def post_month(request, year, month):
    pass

def post_day(request, year, month, day):
    pass

def post_detail(request, year, month, day, slug):
    pass