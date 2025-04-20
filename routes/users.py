from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload
from models import User, UserProfile
from database import session_scope
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('users', __name__)

@bp.route("/", methods=["GET"])
def get_users():
  with session_scope() as session:
    users = session.query(User).options(joinedload(User.profile)).all()
    return jsonify([user.to_dict() for user in users])
  
@bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
  with session_scope() as session:
    user = session.query(User).options(joinedload(User.profile)).get(user_id)
    return jsonify({"error": "User not found"}), 404 if not user else jsonify(user.to_dict())
  
@bp.route("/", methods=["POST"])
def create_user():
  data = request.json
  if not data or not data.get("username") or not data.get("email") or not data.get("password"):
    return jsonify({"error": "Missing required fields"}), 400
  
  with session_scope() as session:
    if session.query(User).filter_by(username=data["username"]).first():
      return jsonify({"error": "Username already exists"}), 400

    if session.query(User).filter_by(email=data["email"]).first():
      return jsonify({"error": "Email already exists"}), 400

    user = User(
      username = data["username"],
      email = data["email"],
      password_hashed = generate_password_hash(data["password"])
    )
    session.add(user)
    session.flush()

    if data.get("profile"):
      profile_data = data["profile"]
      profile = UserProfile(
        user_id = user.id,
        first_name = profile_data.get("first_name"),
        last_name = profile_data.get("last_name"),
        bio = profile_data.get("bio"),
        avatar_url = profile_data.get("avatar_url"),
      )
      session.add(profile)

    return jsonify(user.to_dict()), 201


@bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
  data = request.json
  if not data:
    return jsonify({"error": "no data provided"}), 400
  
  with session_scope() as session:
    user = session.query(User).get(user_id)
    if not user:
      return jsonify({"error": "user not found"}), 404

    if "username" in data and data["username"] != user.username:
      if session.query(User).filter_by(username=data["username"]).first():
        return jsonify({"error": "username already exists"}), 400
      user.username = data["username"]
    
    if "email" in data["email"] != user.email:
      if session.query(User).filter_by(email=data["email"]).first():
        return jsonify({"error": "email already exists"}), 400
      user.email = data["email"]

    if "password" in data:
      user.password_hash = generate_password_hash(data["password"])
    
    if "is_active" in data:
      user.is_active = data["is_active"]
    
    if "profile" in data:
      profile_data = data["profile"]
      if user.profile:
        profile = user.profile
        profile.first_name = profile_data.get("first_name", profile.first_name)
        profile.last_name = profile_data.get("last_name", profile.last_name)
        profile.bio = profile_data.get("bio", profile.bio)
        profile.avatar_url = profile_data.get("avatar_url", profile.avatar_url)
      else:
        profile = UserProfile(
          user_id=user.id,
          first_name=profile_data.get('first_name'),
          last_name=profile_data.get('last_name'),
          bio=profile_data.get('bio'),
          avatar_url=profile_data.get('avatar_url')
        )
        session.add(profile)
    return jsonify(user.to_dict())
  
@bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
  with session_scope() as session:
    user = session.query(User).get(user_id)
    if not user:
      return jsonify({"error": "user not found"}), 404
    
    session.delete(user)
    return jsonify({"message": "user deleted successfully"})
