from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload
from models import Comment
from database import session_scope

bp = Blueprint('comments', __name__)

@bp.route('/', methods=['GET'])
def get_comments():
    post_id = request.args.get('post_id')
    
    with session_scope() as session:
        query = session.query(Comment).options(joinedload(Comment.user))
        if post_id:
            query = query.filter_by(post_id=post_id)
        comments = query.all()
        return jsonify([comment.to_dict() for comment in comments])

@bp.route('/<int:comment_id>', methods=['GET'])
def get_comment(comment_id):
    with session_scope() as session:
        comment = session.query(Comment).options(joinedload(Comment.user)).get(comment_id)
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404
        return jsonify(comment.to_dict())

@bp.route('/', methods=['POST'])
def create_comment():
    data = request.json
    if not data or not data.get('content') or not data.get('user_id') or not data.get('post_id'):
        return jsonify({'error': 'Missing required fields'}), 400

    with session_scope() as session:
        comment = Comment(
            content=data['content'],
            user_id=data['user_id'],
            post_id=data['post_id']
        )
        session.add(comment)
        return jsonify(comment.to_dict()), 201

@bp.route('/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    data = request.json
    if not data or not data.get('content'):
        return jsonify({'error': 'Content is required'}), 400

    with session_scope() as session:
        comment = session.query(Comment).get(comment_id)
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404

        comment.content = data['content']
        return jsonify(comment.to_dict())

@bp.route('/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    with session_scope() as session:
        comment = session.query(Comment).get(comment_id)
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404

        session.delete(comment)
        return jsonify({'message': 'Comment deleted successfully'})
