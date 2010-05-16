# file ontology/models.py
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

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
class Tag(models.Model):
    '''
    Tags for blog entries that can cross relate information between users
    and categories.

    '''

    text = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(max_length=30, unique=True, null=True, blank=True)

    # Because I can't stop myself from adding these fields for some reason.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now_add=True, auto_now=True)

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

class TagCatalog(models.Model):
    """
    Joining model between Tagged items and Tags.  I'm finding this more
    appealing both for performance issues and because tag slugs will be easier
    to maintain if Tags themselves are actually unique.
    
    """
    # What Tag is this referring to.
    tag = models.ForeignKey(Tag)
    # Content Type Stuff for generic relationships.
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

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

    # Because I can't stop myself from adding these fields for some reason.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now_add=True, auto_now=True)

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

class TopicCatalog(models.Model):
    """Joining model between Cataloged Models and Topics."""

    # Actual Topic this applies to.
    topic = models.ForeignKey(Topic)
    # Generic Content Type Items
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')