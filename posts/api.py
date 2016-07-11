import json

from flask import request, Response, url_for
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from posts import app
from .database import session

post_schema = {
    'properties': {
        'title': {
            'type': 'string'
        },
        'body': {
            'type': 'string'
        }
    },
    'required': ['title', 'body']
}

@app.route('/api/posts', methods=['GET'])
@decorators.accept('application/json')
def posts_get():
    ''' get a list of posts '''
    # get the querystring arguments
    title_like = request.args.get('title_like')
    body_like = request.args.get('body_like')
    
    # get and filter the posts from the database
    posts = session.query(models.Post)
    if title_like:
        posts = posts.filter(models.Post.title.contains(title_like))
    if body_like:
        posts = posts.filter(models.Post.body.contains(body_like))
    posts = posts.order_by(models.Post.id)
    
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
    session.commit()
    
    message = 'Successfully deleted post with id {}'.format(id)
    data = json.dumps({'message': message})
    return Response(data, 200, mimetype = 'application/json')
    
@app.route('/api/posts', methods = ['POST'])
@decorators.accept('application/json')
@decorators.require('application/json')
def posts_post():
    ''' add a new post '''
    data = request.json
    
    # check that the JSON supplied is valid
    # if not you return a 422 Unprocessable Entity
    try:
        validate(data, post_schema)
    except ValidationError as error:
        data = {'message': error.message}
        return Response(json.dumps(data), 422, mimetype = 'application/json')
    
    # add the post to the database
    post = models.Post(title = data['title'], body = data['body'])
    session.add(post)
    session.commit()
    
    # return a 201 Created, containing the post as JSON and with the
    # Location header set to the location of the post
    data = json.dumps(post.as_dictionary())
    headers = {'Location': url_for('post_get', id = post.id)}
    return Response(data, 201, headers = headers, mimetype = 'application/json')
    
@app.route('/api/posts/<int:id>', methods = ['PUT'])
@decorators.accept('application/json')
@decorators.require('application/json')
def posts_put(id):
    ''' update an existing post '''
    data = request.json
    
    # check that the JSON supplied is valid
    # if not you return a 422 Unprocessable Entity
    try:
        validate(data, post_schema)
    except ValidationError as error:
        data = {'message': error.message}
        return Response(json.dumps(data), 422, mimetype = 'application/json')
    
    # retrieve the post and return error if it does not exist
    post = session.query(models.Post).get(id)
    
    if not post:
        message = 'Could not find post with id {}'.format(id)
        data = json.dumps({'message': message})
        return Response(data, 404, mimetype = 'application/json')
        
    # update the post
    post.title = data['title']
    post.body = data['body']
    session.commit()
    
    # return a 200 OK, containing the post as JSON and with the
    # Location header set to the location of the post
    data = json.dumps(post.as_dictionary())
    headers = {'Location': url_for('post_get', id = post.id)}
    return Response(data, 200, headers = headers, mimetype = 'application/json')