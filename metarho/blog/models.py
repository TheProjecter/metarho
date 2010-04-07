from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError

from metarho import unique_slugify

PUBLISHED_STATUS = 'P'
UNPUBLISHED_STATUS = 'U'
POST_STATUS = (
               (PUBLISHED_STATUS, 'Published'),
               (UNPUBLISHED_STATUS, 'Unpublished'),
)

# CUSTOM MANAGERS

class PostManager(models.Manager):
    '''
    Adds some features to the default manager for published posts
    published dates.
    
    '''
    
    def published(self, pub_date=None):
        '''
        Only returns posts that are published and of pub_date or earlier.

        :param pub_date: Posts with pub_date later than this are not considered
                         published.

        '''
        if not pub_date:
            pub_date = datetime.now()
        return self.filter(status=PUBLISHED_STATUS, pub_date__lte=pub_date, pub_date__isnull=False)
    
class TagManager(models.Manager):
    '''
    Adds some features for managing tags related to only published posts.
    
    '''
    def published(self, pub_date=None):
        '''
        Only returns tags for published post of pub_date or earlier.

        :param pub_date: Posts with pub_date later than this are not considered
                         published.

        '''
        if not pub_date:
            pub_date = datetime.now()
        return self.filter(post__status=PUBLISHED_STATUS, post__pub_date__lte=pub_date, post__pub_date__isnull=False).distinct()
        
class TopicManager(models.Manager):
    '''
    Adds some features for managing tags related to only published posts.
    
    '''
    def published(self, pub_date=None):
        '''
        Only returns topics for published posts of pub_date or earlier.

        :param pub_date: Posts with pub_date later than this are not considered
                         published.

        '''
        
        if not pub_date:
            pub_date = datetime.now()
        return self.filter(post__status=PUBLISHED_STATUS, post__pub_date__lte=pub_date, post__pub_date__isnull=False).distinct()

# MODELS

class Tag(models.Model):
    '''
    Tags for blog entries that can cross relate information between users
    and categories.
    
    '''
    
    text = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(max_length=30, unique=True)
    objects = TagManager()
    
    def save(self, force_insert=False, force_update=False):
        '''
        Custom save method to handle slugs and such.
        '''
        
        # Create slug if none exists.
        if not self.slug:
            unique_slugify(self, self.text) # Create unique slug if none exists.
     
        super(Tag, self).save(force_insert, force_update) # Actual Save method.
     
    def __unicode__(self):
        return self.text
    
    class Meta:
        ordering = ['text']
        
class Topic(models.Model):
    '''
    Topics form sections and catagories of posts to enable topical based
    conversations.
    
    '''
    text = models.CharField(max_length=75)
    parent = models.ForeignKey('self', null=True, blank=True) # Enable topic structures.
    description = models.TextField(null=True, blank=True)
    slug = models.CharField(max_length=75)
    objects = TopicManager()
    
    def save(self, force_insert=False, force_update=False):
        '''
        Custom save method to handle slugs and such.
        '''
        # Set pub_date if none exist and publish is true.
        if not self.slug:
            qs = Topic.objects.filter(parent=self.parent)
            unique_slugify(self, self.text, queryset=qs) # Unique for each parent.

        # Raise validation error if trying to create slug duplicate under parent.
        if Topic.objects.exclude(pk=self.pk).filter(parent=self.parent, slug=self.slug):
            raise ValidationError("Slugs cannot be duplicated under the same parent topic.")
     
        super(Topic, self).save(force_insert, force_update) # Actual Save method.

    def __unicode__(self):
        return self.text

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['text']
        unique_together = (('text', 'parent'))

class Post(models.Model):
    '''Blog Entries'''

    title = models.CharField(max_length=75)
    slug = models.SlugField(max_length=75, null=True, unique_for_date='pub_date')
    author = models.ForeignKey(User)
    content = models.TextField(null=True)
    teaser = models.TextField(null=True, blank=True)
    pd_help = 'Date to publish.'
    pub_date = models.DateTimeField(help_text=pd_help, null=True, blank=True)
    status = models.CharField(max_length=1, choices=POST_STATUS)
    tags = models.ManyToManyField(Tag, null=True)
    topics = models.ManyToManyField(Topic, null=True)
    created_on = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    last_updated = models.DateTimeField(null=False, blank=False, auto_now=True, auto_now_add=True)
    
    objects = PostManager()

    @models.permalink
    def get_absolute_url(self):
        '''Get projects url.'''
        return reverse('post_detail', args=[self.pub_date.year, self.pud_date.month, self.pub_date.day, self.slug])

    def __unicode__(self):
        return self.title
    
    def clean(self):
        '''
        Provide some custom validation and other tasks.
        
        '''
        # Set pub_date if none exist and publish is true.
        if self.status == PUBLISHED_STATUS and not self.pub_date:
            self.pub_date = datetime.now() # No publishing without a pub_date
            
        # Create slug if none exists and it's published.
        if not self.slug and self.status == PUBLISHED_STATUS:
            qs = Post.objects.published().filter(pub_date__startswith=self.pub_date.date())
            # Slug should be unique for date.
            unique_slugify(self, self.title, queryset=qs)
            
        # Validate unique slug by pub_date.  Unique_for_date only validates at
        # the model form level.
        if self.slug: 
            p = Post.objects.exclude(pk=self.pk).filter(slug=self.slug)
            if self.pub_date:
                p = p.filter(pub_date__startswith=self.pub_date.date())
            else:
                p = p.filter(pub_date__isnull=True)
            # if slug isn't None and a match is found on that date, throw error.
            if p:
                raise ValidationError("Slug must be unique for author and pub_date")

    def save(self, force_insert=False, force_update=False):
        '''
        Custom save method to handle slugs and such.
        @TODO Remove this once if using Django 1.2
        
        '''
        # @NOTE this is a work around until I go to django 1.2
        self.clean()
        super(Post, self).save(force_insert, force_update) # Actual Save method.

    class Meta:
        get_latest_by = 'pub_date'
        ordering = ['-pub_date']

class PostMeta(models.Model):
    '''Holds additional data in key:value pairs for posts.'''
    
    post = models.ForeignKey(Post)
    key = models.CharField(max_length=30, null=False, blank=False)
    value = models.CharField(max_length=255, null=False, blank=False)