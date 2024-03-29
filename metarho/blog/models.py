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
from django.contrib.contenttypes import generic

from metarho import PUBLISHED_STATUS
from metarho import PUB_STATUS
from metarho import unique_slugify
from metarho.ontology.models import TopicCatalog
from metarho.ontology.models import TaggedItem

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
    
class Post(models.Model):
    '''Blog Entries'''

    title = models.CharField(max_length=75)
    slug = models.SlugField(max_length=75, null=True, blank=True, unique_for_date='pub_date')
    author = models.ForeignKey(User)
    content = models.TextField(null=True)
    teaser = models.TextField(null=True, blank=True)
    pd_help = 'Date to publish.'
    pub_date = models.DateTimeField(help_text=pd_help, null=True, blank=True)
    status = models.CharField(max_length=1, choices=PUB_STATUS)
    date_created = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    date_modified = models.DateTimeField(null=False, blank=False, auto_now=True, auto_now_add=True)

    # Reverse Generic Relationships
    topics = generic.GenericRelation(TopicCatalog)
    tags = generic.GenericRelation(TaggedItem)
    
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