from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from agent import db

class User(db.Model, UserMixin): 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    time = db.Column(db.String(100))
    info = db.Column(db.String(200))
    onto = db.Column(db.String(200))