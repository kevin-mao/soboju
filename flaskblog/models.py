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
    db. Column('friend_a_id', db.Integer, db.ForeignKey('user.id'), 
                                        primary_key=True),
    db.Column('friend_b_id', db.Integer, db.ForeignKey('user.id'), 
                                            primary_key=True)
)

class User(Base, db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    friends = db.relationship("User", secondary=friendship, 
                           primaryjoin=id==friendship.c.friend_a_id,
                           secondaryjoin=id==friendship.c.friend_b_id,
    )
    sections = db.relationship("Section", backref="user")

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)