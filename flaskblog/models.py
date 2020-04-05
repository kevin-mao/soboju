from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

friendship = db.Table(
    'friendships', db.metadata,
    db. Column('friend_a_id', db.Integer, db.ForeignKey('user.id'),
                                        primary_key=True),
    db.Column('friend_b_id', db.Integer, db.ForeignKey('user.id'),
                                            primary_key=True)
)

community = db.Table(
    'membership', db.metadata,
    db. Column('community', db.Integer, db.ForeignKey('community.id'),
                                        primary_key=True),
    db.Column('member', db.Integer, db.ForeignKey('user.id'),
                                            primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    pages = db.relationship("Page", backref="user")
    friends = db.relationship("User", secondary=friendship, 
                           primaryjoin=id==friendship.c.friend_a_id,
                           secondaryjoin=id==friendship.c.friend_b_id,
    )
    community = db.relationship("Community", secondary=community, backref="members")

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Community(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pages = db.relationship("Page", backref="community")

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # can be nullable
    community_id = db.Column(db.Integer, db.ForeignKey('community.id')) # can be nullable
    title = db.Column(db.String(100), nullable=False)
    entries = db.relationship("Entry", backref="page")
    goals = db.relationship("Goal", backref="page")

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'), nullable=False)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goals = db.Column(db.String(500), nullable=False)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'), nullable=False)