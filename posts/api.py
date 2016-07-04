import json

from flask import request, Response, url_for
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from posts import app
from .database import session

@app.route('/api/posts', methods=['GET'])
@decorators.accept('application/json')
def posts_get():
    ''' get a list of posts '''
    
    # get the posts from the database
    posts = session.query(models.Post).order_by(models.Post.id)
    
    # convert the posts to JSON and return a response
    data = json.dumps([post.as_dictionary() for post in posts])
    return Response(data, 200, mimetype = 'application/json')
    
@app.route('/api/posts/<int:id>', methods=['GET'])
@decorators.accept('application/json')
def post_get(id):
    ''' single post endpoint '''
    # get the post from the database
    post = session.query(models.Post).get(id)
    
    # check whether the post exists
    # if not return a 404 with a helpful message
    if not post:
        message = 'Could not find post with id {}'.format(id)
        data = json.dumps({'message': message})
        return Response(data, 404, mimetype = 'application/json')
        
    # return the post as JSON
    data = json.dumps(post.as_dictionary())
    return Response(data, 200, mimetype = 'application/json')

@app.route('/api/posts/<int:id>', methods=['DELETE'])
@decorators.accept('application/json')
def post_delete(id):
    ''' delete post '''
    # get the post from the database
    post = session.query(models.Post).get(id)
    if not post:
        message = 'Post with id {} requested for deletion does not exist.'.format(id)
        data = json.dumps({'message': message})
        return Response(data, 404, mimetype = 'application/json')
    
    session.delete(post)
    
    message = 'Successfully deleted post with id {}'.format(id)
    data = json.dumps({'message': message})
    return Response(data, 200, mimetype = 'application/json')