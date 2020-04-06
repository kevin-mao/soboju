from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

friendship = db.Table(
    'friendship', db.metadata,
    db.Column('friend_a_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('friend_b_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

membership = db.Table(
    'membership', db.metadata,
    db.Column('community', db.Integer, db.ForeignKey('community.id'), primary_key=True),
    db.Column('member', db.Integer, db.ForeignKey('user.id'), primary_key=True)
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
                           secondaryjoin=id==friendship.c.friend_b_id)
    community = db.relationship("Community", secondary=membership, backref="members")
    comments = db.relationship("Comment", backref="author")


    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Community(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    pages = db.relationship("Page", backref="community")

    def __repr__(self):
        return f"Community('{self.name}')"

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # can be nullable
    community_id = db.Column(db.Integer, db.ForeignKey('community.id')) # can be nullable
    title = db.Column(db.String(100), nullable=False)
    entries = db.relationship("Entry", backref="page")
    goals = db.relationship("Goal", backref="page")

    def __repr__(self):
        return f"Page('{self.title}')"

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    comments = db.relationship("Comment", backref="entry")
    
    def __repr__(self):
        return f"Entry('{self.text}')"

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    comments = db.relationship("Comment", backref="goal")

    def __repr__(self):
        return f"Goal('{self.goals}, {self.completed}')"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # the author of this comment
    entry_id = db.Column(db.Integer, db.ForeignKey('entry.id')) # the author of this comment
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id')) # the author of this comment


