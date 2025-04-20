import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# user-role association table
user_roles = Table('user_roles', Base.metadata,
  Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),                   
  Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),                   
)

# post-tag association table
post_tags = Table('post_tags', Base.metadata,
  Column('post_id', Integer, ForeignKey('posts.id', ondelete="CASCADE"), primary_key=True),                  
  Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE"), primary_key=True),                  
)

class User(Base):
  __tablename__ = 'users'

  id = Column(Integer, primary_key=True)
  username = Column(String(20), unique=True, nullable=False)
  email = Column(String(120), unique=True, nullable=False)
  password_hash = Column(String(128))
  created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
  is_active = Column(Boolean, default=True)

  posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
  comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
  roles = relationship("Role", secondary=user_roles, back_populates="users")
  profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

  def to_dict(self):
    return {
      "id": self.id,
      "username": self.username,
      "email": self.email,
      "created_at": datetime.datetime.isoformat(self.created_at) if self.created_at else None,
      "is_active": self.is_active
    }
  
class UserProfile(Base):
  __tablename__ = "user_profile"

  id = Column(Integer, primary_key=True)
  user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True)
  first_name = Column(String(50))
  last_name = Column(String(50))
  bio = Column(String(500))
  avatar_url = Column(String(255))

  user = relationship("User", back_populates="profile")

  def to_dict(self):
    return {
      'id': self.id,
      'user_id': self.user_id,
      'first_name': self.first_name,
      'last_name': self.last_name,
      'bio': self.bio,
      'avatar_url': self.avatar_url
    }
  
class Comment(Base):
  __tablename__ = "comments"

  id = Column(Integer, primary_key=True)
  content = Column(String, nullable=False)
  created_at = Column(DateTime, default=datetime.timezone.utc)
  user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
  post_id = Column(Integer, ForeignKey('posts.id', ondelete="CASCADE"))

  user = relationship("User", back_populates="comments")
  post = relationship("Post", back_populates="comments")

  def to_dict(self):
    return {
      'id': self.id,
      'content': self.content,
      'created_at': datetime.datetime.isoformat(self.created_at) if self.created_at else None,
      'user_id': self.user_id,
      'post_id': self.post_id,
      'user': self.user.to_dict() if self.user else None 
    }
  
class Role(Base):
  __tablename__ = "roles"

  id = Column(Integer, primary_key=True)
  name = Column(String(50), unique=True, nullable=False)
  description = Column(String(200))

  users = relationship("User", secondary=user_roles, back_populates="roles")

  def to_dict(self):
    return {
      "id": self.id,
      "name": self.name,
      "description": self.description
    }
  
class Tag(Base):
  __tablename__ = "tags"
  id = Column(Integer, primary_key=True)
  name = Column(String(50), unique=True, nullable=False)
    
  posts = relationship("Post", secondary=post_tags, back_populates="tags")
  
  def to_dict(self):
    return {
        'id': self.id,
        'name': self.name
    }
  
class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.timezone.utc)
    updated_at = Column(DateTime, default=datetime.timezone.utc, onupdate=datetime.timezone.utc)
    author_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'author_id': self.author_id,
            'author': self.author.to_dict() if self.author else None,
            'tags': [tag.to_dict() for tag in self.tags] if self.tags else []
        }