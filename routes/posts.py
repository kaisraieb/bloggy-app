from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload
from models import Post, Tag
from database import session_scope

bp = Blueprint('posts', __name__)

@bp.route('/', methods=['GET'])
def get_posts():
    with session_scope() as session:
        posts = session.query(Post).options(
            joinedload(Post.author),
            joinedload(Post.tags),
            joinedload(Post.comments)
        ).all()
        return jsonify([post.to_dict() for post in posts])
    
@bp.route('/<int:post_id>', methods=['GET'])
def get_post(post_id):
    with session_scope() as session:
        post = session.query(Post).options(
            joinedload(Post.author),
            joinedload(Post.tags),
            joinedload(Post.comments)
        ).get(post_id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        return jsonify(post.to_dict())
    
@bp.route('/', methods=['POST'])
def create_post():
    data = request.json
    if not data or not data.get('title') or not data.get('content') or not data.get('author_id'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    with session_scope() as session:
        post = Post(
            title=data['title'],
            content=data['content'],
            author_id=data['author_id']
        )
        session.add(post)
        session.flush()
        
        if data.get('tags'):
            for tag_name in data['tags']:
                tag = session.query(Tag).filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    session.add(tag)
                post.tags.append(tag)
        
        return jsonify(post.to_dict()), 201
    
@bp.route('/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    with session_scope() as session:
        post = session.query(Post).get(post_id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        if 'title' in data:
            post.title = data['title']
        
        if 'content' in data:
            post.content = data['content']
        
        if 'tags' in data:
            post.tags.clear()
            for tag_name in data['tags']:
                tag = session.query(Tag).filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    session.add(tag)
                post.tags.append(tag)
        
        return jsonify(post.to_dict())
    
@bp.route('/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    with session_scope() as session:
        post = session.query(Post).get(post_id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        session.delete(post)
        return jsonify({'message': 'Post deleted successfully'})