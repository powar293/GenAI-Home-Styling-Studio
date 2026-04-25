from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    designs = db.relationship('Design', backref='user', lazy=True)
    bookings = db.relationship('Booking', backref='user', lazy=True)

class Design(db.Model):
    __tablename__ = 'designs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_path = db.Column(db.String(256), default='')
    style = db.Column(db.String(50), nullable=False)
    suggestions_json = db.Column(db.Text, default='{}')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Furniture(db.Model):
    __tablename__ = 'furniture'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    style_tags = db.Column(db.String(200), default='')
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(300), default='')
    description = db.Column(db.Text, default='')

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    furniture_id = db.Column(db.Integer, db.ForeignKey('furniture.id'), nullable=False)
    design_id = db.Column(db.Integer, db.ForeignKey('designs.id'), nullable=True)
    status = db.Column(db.String(30), default='confirmed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    furniture = db.relationship('Furniture', backref='bookings')
    design = db.relationship('Design', backref='bookings')
