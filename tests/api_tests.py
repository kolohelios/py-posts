import unittest
import os
import json
try: from urllib.parse import urlparse
except ImportError: from urlparse import urlparse # Python 2 compatibility

# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "posts.config.TestingConfig"

from posts import app
from posts import models
from posts.database import Base, engine, session

class TestAPI(unittest.TestCase):
    """ Tests for the posts API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)
        
    def test_get_empty_posts(self):
        ''' getting posts from an empty database '''
        response = self.client.get('/api/posts',
            headers = [('Accept', 'application/json')]
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/json')
        
        data = json.loads(response.data.decode('ascii'))
        self.assertEqual(data, [])
        
    def test_get_posts(self):
        ''' getting posts from a populated database '''
        postA = models.Post(title = 'Example Post A', body = 'Just a test')
        postB = models.Post(title = 'Example Post B', body = 'Still a test')
        
        session.add_all([postA, postB])
        session.commit()
        
        response = self.client.get('/api/posts',
            headers = [('Accept', 'application/json')]
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/json')
        
        data = json.loads(response.data.decode('ascii'))
        self.assertEqual(len(data), 2)
        
        postA = data[0]
        self.assertEqual(postA['title'], 'Example Post A')
        self.assertEqual(postA['body'], 'Just a test')
        
        postB = data[1]
        self.assertEqual(postB['title'], 'Example Post B')
        self.assertEqual(postB['body'], 'Still a test')
        
    def test_get_post(self):
        ''' getting a single post from a populated database '''
        
        postA = models.Post(title = 'Example Post A', body = 'Just a test')
        postB = models.Post(title = 'Example Post B', body = 'Still a test')
        
        session.add_all([postA, postB])
        session.commit()
        
        response = self.client.get('/api/posts/{}'.format(postB.id),
            headers = [('Accept', 'application/json')]
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/json')
        
        post = json.loads(response.data.decode('ascii'))
        self.assertEqual(post['title'], 'Example Post B')
        self.assertEqual(post['body'], 'Still a test')
        
    def test_get_non_existent_post(self):
        ''' getting a single post which doesn't exist '''
        response = self.client.get('/api/posts/1',
             headers = [('Accept', 'application/json')]
        )
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, 'application/json')
        
        data = json.loads(response.data.decode('ascii'))
        self.assertEqual(data['message'], 'Could not find post with id 1')
        
    def test_unsupported_accept_header(self):
        response = self.client.get('/api/posts',
            headers = [('Accept', 'application/xml')]
        )
        
        self.assertEqual(response.status_code, 406)
        self.assertEqual(response.mimetype, 'application/json')
        
        data = json.loads(response.data.decode('ascii'))
        self.assertEqual(data['message'],
            'Request must accept application/json data')
    
    def test_delete_post(self):
        postA = models.Post(title = 'Example Post A', body = 'Just a test')
        # postB = models.Post(title = 'Example Post B', body = 'Still a test')
        
        session.add(postA)
        session.commit()
        
        response = self.client.delete('/api/posts/{}'.format(postA.id),
            headers = [('Accept', 'application/json')]
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/json')
        
    def test_delete_non_existent_post(self):
        postA = models.Post(title = 'Example Post A', body = 'Just a test')
        
        session.add(postA)
        session.commit()
        
        response = self.client.delete('/api/posts/2',
            headers = [('Accept', 'application/json')]
        )
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, 'application/json')
        
        data = json.loads(response.data.decode('ascii'))
        self.assertEqual(data['message'],
            'Post with id 2 requested for deletion does not exist.')
            
    def test_get_posts_with_title(self):
        ''' filtering posts by title '''
        postA = models.Post(title = "Post with bells", body = "Just a test")
        postB = models.Post(title = "Post with whistles", body = "Still a test")
        postC = models.Post(title = "Post with bells and whistles",
                            body = "Another test")

        session.add_all([postA, postB, postC])
        session.commit()

        response = self.client.get("/api/posts?title_like=whistles",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        posts = json.loads(response.data.decode("ascii"))
        self.assertEqual(len(posts), 2)

        post = posts[0]
        self.assertEqual(post["title"], "Post with whistles")
        self.assertEqual(post["body"], "Still a test")

        post = posts[1]
        self.assertEqual(post["title"], "Post with bells and whistles")
        self.assertEqual(post["body"], "Another test")
        
    def test_get_posts_with_body(self):
        ''' filtering posts by body '''
        postA = models.Post(title = "Post with bells", body = "Just a test")
        postB = models.Post(title = "Post with whistles", body = "Still a test")
        postC = models.Post(title = "Post with bells and whistles",
                            body = "Another test")

        session.add_all([postA, postB, postC])
        session.commit()

        response = self.client.get("/api/posts?body_like=Another",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        posts = json.loads(response.data.decode("ascii"))
        self.assertEqual(len(posts), 1)

        post = posts[0]
        self.assertEqual(post["title"], "Post with bells and whistles")
        self.assertEqual(post["body"], "Another test")
        
    def test_get_posts_with_title_and_body(self):
        ''' filtering posts by title and body '''
        postA = models.Post(title = "Post with bells", body = "Just a test")
        postB = models.Post(title = "Post with whistles", body = "Still a test")
        postC = models.Post(title = "Post with bells and whistles",
                            body = "Another test")

        session.add_all([postA, postB, postC])
        session.commit()

        response = self.client.get("/api/posts?body_like=Another&title_like=bells",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        posts = json.loads(response.data.decode("ascii"))
        self.assertEqual(len(posts), 1)

        post = posts[0]
        self.assertEqual(post["title"], "Post with bells and whistles")
        self.assertEqual(post["body"], "Another test")
        
    def test_post_post(self):
        ''' posting a new post '''
        data = {
            'title': 'Example Post',
            'body': 'Just a test'
        }
        
        response = self.client.post('/api/posts',
            data = json.dumps(data),
            content_type = 'application/json',
            headers = [('Accept', 'application/json')]
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, 'application/json')
        self.assertEqual(urlparse(response.headers.get('Location')).path,
            '/api/posts/1')
        
        data = json.loads(response.data.decode('ascii'))
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['title'], 'Example Post')
        self.assertEqual(data['body'], 'Just a test')
        
        posts = session.query(models.Post).all()
        self.assertEqual(len(posts), 1)
        
        post = posts[0]
        self.assertEqual(post.title, 'Example Post')
        self.assertEqual(post.body, 'Just a test')
        
    def test_post_unsupported_mimetype(self):
        data = '<xml></xml>'
        response = self.client.post('/api/posts',
            data = json.dumps(data),
            content_type = 'application/xml',
            headers = [('Accept', 'application/json')]
        )
        
        self.assertEqual(response.status_code, 415)
        self.assertEqual(response.mimetype, 'application/json')
        
        data = json.loads(response.data.decode('ascii'))
        self.assertEqual(data['message'],
            'Request must contain application/json data')
            
    def test_post_invalid_data(self):
        ''' posting a post with an invalid body '''
        data = {
            'title': 'Example Post',
            'body': 32
        }
        
        response = self.client.post('/api/posts',
            data = json.dumps(data),
            content_type = 'application/json',
            headers = [('Accept', 'application/json')]
        )

        self.assertEqual(response.status_code, 422)
        
        data = json.loads(response.data.decode('ascii'))
        self.assertEqual(data['message'], '32 is not of type \'string\'')
        
    def test_post_missing_data(self):
        ''' posting a post with a missing body '''
        data = {
            'title': 'Example Post',
        }
        
        response = self.client.post('/api/posts',
            data = json.dumps(data),
            content_type = 'application/json',
            headers = [('Accept', 'application/json')]
        )
        
        self.assertEqual(response.status_code, 422)
        
        data = json.loads(response.data.decode('ascii'))
        self.assertEqual(data['message'], '\'body\' is a required property')
        
    def test_post_put(self):
        ''' putting a post '''
        
        # first we need to create a post to update
        data = {
            'title': 'Example Post',
            'body': 'Just a test'
        }
        
        response = self.client.post('/api/posts',
            data = json.dumps(data),
            content_type = 'application/json',
            headers = [('Accept', 'application/json')]
        )
        
        data = {
            'title': 'Changed Title',
            'body': 'And changed body.'
        }
        
        response = self.client.put('/api/posts/1',
            data = json.dumps(data),
            content_type = 'application/json',
            headers = [('Accept', 'application/json')]
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/json')
        self.assertEqual(urlparse(response.headers.get('Location')).path,
            '/api/posts/1')
        
        data = json.loads(response.data.decode('ascii'))
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['title'], 'Changed Title')
        self.assertEqual(data['body'], 'And changed body.')
        
        posts = session.query(models.Post).all()
        self.assertEqual(len(posts), 1)
        
        post = posts[0]
        self.assertEqual(post.title, 'Changed Title')
        self.assertEqual(post.body, 'And changed body.')
        
    def test_post_put_with_nonexistent_id(self):
        data = {
            'title': 'Changed Title',
            'body': 'And changed body.'
        }
        
        response = self.client.put('/api/posts/1',
            data = json.dumps(data),
            content_type = 'application/json',
            headers = [('Accept', 'application/json')]
        )
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, 'application/json')
        
        data = json.loads(response.data.decode('ascii'))
        self.assertEqual(data['message'], 'Could not find post with id 1')
        
    def test_put_unsupported_mimetype(self):
        data = '<xml></xml>'
        response = self.client.put('/api/posts/1',
            data = json.dumps(data),
            content_type = 'application/xml',
            headers = [('Accept', 'application/json')]
        )
        
        self.assertEqual(response.status_code, 415)
        self.assertEqual(response.mimetype, 'application/json')
        
        data = json.loads(response.data.decode('ascii'))
        self.assertEqual(data['message'],
            'Request must contain application/json data')
            
    def test_put_invalid_data(self):
        ''' putting a post with an invalid body '''
        data = {
            'title': 'Example Post',
            'body': 32
        }
        
        response = self.client.put('/api/posts/1',
            data = json.dumps(data),
            content_type = 'application/json',
            headers = [('Accept', 'application/json')]
        )

        self.assertEqual(response.status_code, 422)
        
        data = json.loads(response.data.decode('ascii'))
        self.assertEqual(data['message'], '32 is not of type \'string\'')
        
    def test_put_missing_data(self):
        ''' posting a post with a missing body '''
        data = {
            'title': 'Example Post',
        }
        
        response = self.client.put('/api/posts/1',
            data = json.dumps(data),
            content_type = 'application/json',
            headers = [('Accept', 'application/json')]
        )
        
        self.assertEqual(response.status_code, 422)
        
        data = json.loads(response.data.decode('ascii'))
        self.assertEqual(data['message'], '\'body\' is a required property')
        
if __name__ == "__main__":
    unittest.main()
