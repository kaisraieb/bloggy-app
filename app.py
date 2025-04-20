from flask import Flask, jsonify
from flask_cors import CORS
from database import engine, Base
from routes import users, posts, comments

app = Flask(__name__)
CORS(app)

Base.metadata.create_all(engine)

app.register_blueprint(users.bp, url_prefix="/api/users")
app.register_blueprint(posts.bp, url_prefix="/api/posts")
app.register_blueprint(comments.bp, url_prefix="/api/comments")

@app.errorhandler(404)
def not_found(error):
  return jsonify({'error': "Not Found"}), 404

@app.errorhandler(500)
def internal_error(error):
  return jsonify({'error': "Internal Server Error"}), 500

if __name__ == "__main__":
  app.run(debug=True, port=5000)
