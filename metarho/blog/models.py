# file models.py
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
    slug = models.SlugField(max_length=30, unique=True, null=True, blank=True)
    objects = TagManager()

    def weight(self):
        '''Returns the percent of posts this tag applies to.'''
        post_total = Post.objects.published().count()
        tag_total = Post.objects.published().filter(tags=self.text).count()

        return tag_total/post_total

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
    # Can be null and blank because it will get auto generated on save if so.
    slug = models.CharField(max_length=75, null=True, blank=True)
    path = models.CharField(max_length=255, blank=True)

    # Custom manager for returning published posts.
    objects = TopicManager()

    def get_path(self):
        '''
        Constructs the path value for this topic based on hierarchy.
        
        '''
        ontology = []
        target = self.parent
        while(target is not None):
           ontology.append(target.slug)
           target = target.parent
        ontology.append(self.slug)
        return '%s/' % '/'.join(ontology) # Needs a trailing slash too.


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

        self.path = self.get_path() # Rebuild the path attribute whenever saved.
     
        super(Topic, self).save(force_insert, force_update) # Actual Save method.

    def __unicode__(self):
        '''Returns the name of the Topic as a it's chained relationship.'''
        ontology = []
        target = self.parent
        while(target is not None):
           ontology.append(target.text)
           target = target.parent
        ontology.append(self.text)
        return ' - '.join(ontology)

    class Meta:
        ordering = ['path']
        unique_together = (('slug', 'parent'), ('text', 'parent'))

class Publication(models.Model):
    '''
    This sets up a Publication that posts are related to.  The term Publication 
    is intentially vague and can mean a Blog, Column or something else. 
    
    '''
    title = models.CharField(max_length=75)
    slug = models.SlugField(max_length=75, unique=True, blank=True)
    owner = models.ForeignKey(User)
    default = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)
    copyright = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        '''Return the title of the publication by default.'''
        return self.title

    def save(self, force_insert=False, force_update=False):
        '''Custom save method slugifies the title if one is not created.'''

        if self.default: # Make sure there is only one default Publication.
            Publication.objects.all().update(default=False)

        if not self.slug:
             unique_slugify(self, self.title)
        super(Publication, self).save(force_insert, force_update)

class Post(models.Model):
    '''Blog Entries'''

    title = models.CharField(max_length=75)
    # @TODO Make slug unique for publication on date.
    slug = models.SlugField(max_length=75, null=True, blank=True, unique_for_date='pub_date')
    author = models.ForeignKey(User)
    publication = models.ForeignKey(Publication)
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
        return reverse('blog:post-detail', args=[self.pub_date.year, self.pud_date.month, self.pub_date.day, self.slug])

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