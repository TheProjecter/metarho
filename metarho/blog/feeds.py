from django.contrib.syndication.feeds import Feed
from django.utils import feedgenerator
from django.core.urlresolvers import reverse


from metarho.blog.models import Post

class LatestPostsFeed(Feed):
    '''
    Returns the latests posts in RSS format.
    
    Each atrribute has alternate ways they can be called in a feed.  See 
    `Django Syndication Famework 
    <http://docs.djangoproject.com/en/dev/ref/contrib/syndication/>`_ for more 
    information.
    
    '''

    feed_type = feedgenerator.Rss201rev2Feed

    # These have alternate ways they can be called in a feed.  See `Django
    # Syndication Famework <http://docs.djangoproject.com/en/dev/ref/contrib/syndication/>`
    title = "I need a title"
    link = "/sitenews/"
    description = "Updates on changes and additions to chicagocrime.org."
    author_name = 'Scott Turnbull'
    author_email = 'streamweaver@flagonwiththedragon.com' # Hard-coded author e-mail.
    author_link = 'http://www.flagonwiththedragon.com' # Hard-coded author URL.
    feed_copyright = 'Copyright (c) 2007, Sally Smith' # Hard-coded copyright notice.
    item_copyright = feed_copyright
    ttl = 600 # Hard-coded Time To Live.

    def items(self):
        """
        Returns a list of items to publish in this feed.

        """
        posts = Post.objects.published().order_by('-pub_date')
        return posts[:10]

    def item_title(self, item):
        """
        Takes an item, as returned by items(), and returns the item's
        title as a normal Python string.
        
        """
        return item.title

    def item_description(self, item):
        """
        Takes an item, as returned by items(), and returns the item's
        description as a normal Python string.

        """
        return item.content

    def item_link(self, item):
        """
        Takes an item, as returned by items(), and returns the item's URL.
        
        """
        return reverse('blog:post-detail', args=[item.pub_date.year, item.pub_date.strftime('%b'), item.pub_date.day, item.slug])
    
    def item_author_name(self, item):
        """
        Takes an item, as returned by items(), and returns the item's
        author's name as a normal Python string.
        """
        name = item.author.username
        if item.author.get_full_name():
            name = item.author.get_full_name()
        return name

    def item_author_email(self, obj):
        """
        Takes an item, as returned by items(), and returns the item's
        author's e-mail as a normal Python string.
        
        """
        return obj.author.email

    def item_author_link(self, obj):
        """
        Takes an item, as returned by items(), and returns the item's
        author's URL as a normal Python string.

        """
        return self.link # @TODO Make this link to userprofile when available.

    def item_pubdate(self, item):
        """
        Takes an item, as returned by items(), and returns the item's
        pubdate.

        """
        return item.pub_date

    def item_categories(self, item):
        """
        Takes an item, as returned by items(), and returns the item's
        categories.
        
        """
        cats = [topic.text for topic in item.topics.published()]
        return cats.extend([tag.text for tag in item.tags.published()])

class LatestPostsFeedAtom(LatestPostsFeed):

    feed_type = feedgenerator.Atom1Feed
    subtitle = LatestPostsFeed.description
