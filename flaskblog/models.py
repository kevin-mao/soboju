from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

friendship = db.Table(
    'friendships', Base.metadata,
    db. Column('friend_a_id', db.Integer, db.ForeignKey('User.id'),
                                        primary_key=True),
    db.Column('friend_b_id', db.Integer, db.ForeignKey('User.id'),
                                            primary_key=True)
)

class User(Base, db.Model, UserMixin):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    friends = db.relationship("User", secondary=friendship, 
                           primaryjoin=id==friendship.c.friend_a_id,
                           secondaryjoin=id==friendship.c.friend_b_id,
    )
    pages = db.relationship("Page", backref="User")

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Page(Base, db.Model):
    __tablename__ = 'Page'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    entries = db.relationship("Entry", backref="Page")
    goals = db.relationship("Goal", backref="Page")

class Entry(Base, db.Model):
    __tablename__ = 'Entry'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Page.id'), nullable=False)

class Goal(Base, db.Model):
    __tablename__ = 'Goal'
    id = db.Column(db.Integer, primary_key=True)
    list = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Page.id'), nullable=False)