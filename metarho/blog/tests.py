from datetime import datetime
from datetime import timedelta

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client

from metarho.blog.models import Post
from metarho.blog.models import Tag
from metarho.blog.models import Topic
from metarho.blog.importer import WordPressExportParser

# CUSTOM MANAGER TESTS

class PostManagerTest(TestCase):
    '''Tests methods related to the custom post manager.'''
    
    fixtures = ['auth.json', 'blog.json']
    
    def setUp(self):
        # Define a default users.
        self.author = User(username='Fakeuser', email='fakeuser@email.com')
        self.author.save()
    
    def test_published(self):
        '''Tests that only published posts are returned.'''
        actual = Post.objects.all().count()
        expected = 3 # 3 total posts of all status
        self.failUnlessEqual(expected, actual, 'Expected %s posts and returned %s!' % (expected, actual))

        actual = Post.objects.published().count()
        expected = 1 # Only one published.
        self.failUnlessEqual(expected, actual, 'Expected %s posts and returned %s!' % (expected, actual))

        # Create a new post with a future publish date
        p = Post(title='test', content='test', status='P')
        p.author = self.author
        p.save()
        actual = Post.objects.published().count()
        expected = 2 # Pubdate defaults to now.
        self.failUnlessEqual(expected, actual, 'Expected %s posts and returned %s!' % (expected, actual))

        p.pub_date = datetime.now() + timedelta(days=1)
        p.save()
        actual = Post.objects.published().count()
        expected = 1 # Should now be 1 with postdated pub_date.
        self.failUnlessEqual(expected, actual, 'Expected %s posts and returned %s!' % (expected, actual))

class TagManagerTest(TestCase):
    '''
    Testing out returns of tags only related to  posts.
    
    '''
    
    fixtures = ['auth.json', 'blog.json']
    
    def setUp(self):
        '''Setup some related objects to test.'''
        self.author = User(username='Fakeuser', email='fakeuser@email.com')
        self.author.save()
        # postdated post to test
        self.pd = Post(title='post dated', content='test', status='P', author=self.author)
        self.pd.pub_date = datetime.now() + timedelta(days=1)
        self.pd.author = self.author
        self.pd.save()
        self.pd.tags.add(Tag.objects.get(slug='funny'))
        self.pd.save()
        # un post to test.
        self.up = Post(title='un', content='test', status='U', author=self.author)
        self.up.author = self.author
        self.up.save()
        self.up.tags.add(Tag.objects.get(slug='cats'))
        self.up.save()    
        
    def test_(self):
        '''Make sure only tags related to  posts appear.'''
        # Test all Tags first
        expected = 30
        actual = Tag.objects.all().count()
        self.failUnlessEqual(expected, actual, 'Expected %s total tags and returned %s' % (expected, actual))
        
        # Test tags for  posts.
        expected = 1
        actual = Tag.objects.published().count()
        self.failUnlessEqual(expected, actual, 'Expected %s  tags and returned %s' % (expected, actual))

        # Set pd pub_date to now.
        self.pd.pub_date = datetime.now()
        self.pd.save()
        expected = 2
        actual = Tag.objects.published().count()
        self.failUnlessEqual(expected, actual, 'Expected %s  tags and returned %s' % (expected, actual))

        # Set up to  and should now be 3
        self.up.status = 'P'
        self.up.save()
        expected = 3
        actual = Tag.objects.published().count()
        self.failUnlessEqual(expected, actual, 'Expected %s  tags and returned %s' % (expected, actual))

class TopicManagerTest(TestCase):
    '''
    Testing out returns of tags only related to  posts.
    
    '''
    
    fixtures = ['auth.json', 'blog.json']
    
    def setUp(self):
        '''Setup some related objects to test.'''
        # Add some more topics to test.
        self.t1 = Topic(text='Test1')
        self.t1.save()
        self.t2 = Topic(text='Test2')
        self.t2.save()
        # Create a temp author for posts.
        self.author = User(username='Fakeuser', email='fakeuser@email.com')
        self.author.save()
        # postdated post to test
        self.pd = Post(title='post dated', content='test', status='P', author=self.author)
        self.pd.pub_date = datetime.now() + timedelta(days=1)
        self.pd.author = self.author
        self.pd.save()
        self.pd.topics.add(self.t1)
        self.pd.save()
        # un post to test.
        self.up = Post(title='un', content='test', status='U', author=self.author)
        self.up.author = self.author
        self.up.save()
        self.up.topics.add(self.t2)
        self.up.save()    
        
    def test_(self):
        '''Make sure only topics related to  posts appear.'''
        # Test all Tags first
        expected = 3
        actual = Topic.objects.all().count()
        self.failUnlessEqual(expected, actual, 'Expected %s total topics and returned %s' % (expected, actual))
        
        # Test tags for  posts.
        expected = 1
        actual = Topic.objects.published().count()
        self.failUnlessEqual(expected, actual, 'Expected %s  topics and returned %s' % (expected, actual))

        # Set pd pub_date to now.
        self.pd.pub_date = datetime.now()
        self.pd.save()
        expected = 2
        actual = Topic.objects.published().count()
        self.failUnlessEqual(expected, actual, 'Expected %s  topics and returned %s' % (expected, actual))

        # Set up to  and should now be 3
        self.up.status = 'P'
        self.up.save()
        expected = 3
        actual = Topic.objects.published().count()
        self.failUnlessEqual(expected, actual, 'Expected %s  topics and returned %s' % (expected, actual))

# MODELS TESTS

class TagTest(TestCase):
    '''Tag Model tests.'''
    def test_save(self):
        '''Just testing that autoslugify works.'''
        tag = Tag(text='Test Me 2/ See IF it (works)')
        tag.save()
        expected = 'test-me-2-see-if-it-works'
        actual = tag.slug
        self.failUnlessEqual(expected, actual, 'Expected %s but slug was %s'% (expected, actual))
        
class TopicTest(TestCase):
    '''Topic Model tests.'''
    def test_save(self):
        '''Make sure slugify works and is unique only per parent.'''
        
        # Parent tests basic slug creation.
        parent = Topic(text='Parent')
        parent.save()
        expected = 'parent'
        actual = parent.slug
        self.failUnlessEqual(expected, actual, 'Parent slug was %s but expected %s' % (actual, expected))

        # Child tests slug with parent.
        child = Topic(text='Child', parent=parent)
        child.save()
        expected = 'child'
        actual = child.slug
        self.failUnlessEqual(actual, expected, 'Child slug was %s but expected %s' % (actual, expected))

        # Child2 tests slug with same name under same parent.
        child2 = Topic(text='Child', parent=parent)
        try:
            child2.save()
            result = False
        except:
            result = True
        self.assertTrue(result, "Unique Together attribute of Topic failed.")
        
        # Try one with different parent name but same child name as another parent.
        parent2 = Topic(text='Parent2')
        parent2.save()
        child3 = Topic(text='Child', parent=parent2)
        child3.save()
        expected = 'child'
        actual = child3.slug
        self.failUnlessEqual(actual, expected, 'Child3 slug was %s but expected %s' % (actual, expected))
        
class PostTest(TestCase):
    def test_save(self):
        """Tests the custom save method."""
        
        user = User(username='Fakeuser', password='notgood', email='fakeuser@email.com')
        user.save()
        
        user2 = User(username='Fakeuser2', password='notgoodeither', email='fu2@email.com')
        user2.save()
        
        p = {
             'title': 'Test Title (1)',
             'author': user,
             'content': 'some content',
             'status': 'U'
             }
        
        post1 = Post(**p)
        post1.save()
        
        # Initially No Slug or pub_date should be assigned.
        self.failUnlessEqual(post1.slug, None, 'Post1 slug was %s when it should be None' % post1.slug)
        self.failUnless(not post1.pub_date, 'PubDate is not Null!')

        # Publishing it should give it a slug and pub_date automatically.
        post1.status = 'P'
        post1.save()
        slugexp = 'test-title-1' 
        slugact = post1.slug
        self.failUnlessEqual(slugexp, slugact, 'Slug was %s but expected %s' % (slugact, slugact))
        self.failUnless(post1.pub_date, 'Post1 pub_date was not set!')
 
        # Set the pub_date back to setup next test.
        new_date = datetime.now() - timedelta(days=1) - timedelta(hours=2)
        post1.pub_date = new_date
        post1.save()
        
        # Setup another post with old pubdate, then change to now to see what happens.
        # Test some slug collisions and such.
        p2 = p.copy()
        p2['status'] = 'P'
        post2 = Post(**p2)
        post2.save()
        
        # Test the slugify feature
        slug = 'test-title-1' 
        self.failUnlessEqual(slug, post2.slug, 'Post2 slug was %s but expected %s' % (post2.slug, slug))
 
        # Now change the pub_date to match p1 and see if it throws a validation error.
        post2.pub_date = datetime.now() - timedelta(days=1) - timedelta(hours=1)
        self.assertRaises(ValidationError, post2.save)
        
        # Test the auto-increment feature of the unique_slugify method.
        post2.slug = None
        post2.save()
        expected = 'test-title-1-2'
        self.failUnlessEqual(post2.slug, expected, 'Post2 slug was %s but expected %s' % (post2.slug, expected))
        
class WordPressExportParserTest(TestCase):
    '''Tests the import scripts'''
    
    def setUp(self):
        file = 'blog/fixtures/wordpress.test.xml'
        self.wp = WordPressExportParser(file)
        
    def test_import_tags(self):
        '''Tests the Tag Import'''
        self.wp.import_tags()
        expected = 30
        actual = Tag.objects.all().count()
        self.failUnlessEqual(expected, actual, 'Expected %s and return %s Tags.' % (expected, actual))
  
    def test_import_topics(self):
        '''Test the import of Topics.'''
        self.wp.import_catagories()
        expected = 2
        actual = Topic.objects.all().count()
        self.failUnlessEqual(expected, actual, 'Expected %s and returned %s Topics.' % (expected, actual))
  
    def test_import_posts(self):
        '''Tests the Import of posts.'''
        
        # Make a user to assign as an author.
        user = User(username='Fakeuser', password='notgood', email='fakeuser@email.com')
        user.save()
        
        # Start with zero posts.
        posts = Post.objects.published()
        expected = 0
        actual = posts.count()
        self.failUnlessEqual(expected, actual, 'Expected %s posts and parsed %s.' % (expected, actual))
        
        # Import the blog entries.
        self.wp.import_catagories()
        self.wp.import_tags()
        self.wp.import_posts()
        posts = Post.objects.all()
        expected = 4
        actual = posts.count()
        self.failUnlessEqual(expected, actual, 'Imported %s posts but expected %s.' % (actual, expected))
        
        # Test creation of post meta and 
        testpost  = Post.objects.get(slug='here-we-go')
        
        # Test PostMeta being created correctly.
        postmeta = testpost.postmeta_set.all()
        expected = 13
        actual = postmeta.count()
        self.failUnlessEqual(expected, actual, 'Expected %s and returned %s Post Meta attributes.' % (expected, actual))
    
        # Test Tags being created and related correctly.
        tagcount = testpost.tags.count()

        expected = 1
        self.failUnlessEqual(expected, tagcount, 'Expected %s and returned %s tags.' % (expected, tagcount))
        
        # Test Topics being created and related correctly.
        topiccount = testpost.topics.all().count()
        expected = 1
        self.failUnlessEqual(expected, topiccount, 'Expected %s and returned %s topics.' % (expected, topiccount))
        
class ViewTest(TestCase):
    '''
    Tests the various views returned  by the app.
    
    user:  Julius
    pw: hailme
    email: ceasar@rome.org
    
    '''
    
    fixtures = ['loremfixtures.json']
    
    def setUp(self):
        self.client = Client()
    
    def test_post_detail(self):
        '''Tests individual entry return.'''
        # Test a published post.
        attrs = ['2009', 'Apr', '08', 'its-all-greek-to-you']
        url = reverse('blog:post-detail', args=attrs)
        expected = 200
        code = self.client.get(url).status_code
        self.failUnlessEqual(code, expected, 'Expected %s but returned %s for %s' % (expected, code, url))
        
        # Test a published post.
        attrs = ['2010', 'Mar', '23', 'maecenas-varius']
        url = reverse('blog:post-detail', args=attrs)
        expected = 404
        code = self.client.get(url).status_code
        self.failUnlessEqual(code, expected, 'Expected %s but returned %s for %s' % (expected, code, url))
        
    def test_wp_redirect(self):
        '''
        Tests the wp_post_redirect decorator.
        
        '''
        expected = 301
        url = '?p=4'
        code = self.client.get(url).status_code
        self.failUnlessEqual(code, expected, 'Expected %s but returned %s for %s' % (expected, code, url))