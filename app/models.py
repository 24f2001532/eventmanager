from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'organizer' or 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    organized_events = db.relationship('Event', backref='organizer', lazy=True, foreign_keys='Event.organizer_id')
    registrations = db.relationship('Registration', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    registration_deadline = db.Column(db.DateTime, nullable=False)
    max_registrations = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    registrations = db.relationship('Registration', backref='event', lazy=True, cascade='all, delete-orphan')
    
    @property
    def registration_count(self):
        return len(self.registrations)
    
    @property
    def is_registration_open(self):
        return datetime.utcnow() < self.registration_deadline
    
    @property
    def is_full(self):
        if self.max_registrations is None:
            return False
        return self.registration_count >= self.max_registrations
    
    def __repr__(self):
        return f'<Event {self.title}>'

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure one user can only register once per event
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='unique_user_event_registration'),)
    
    def __repr__(self):
        return f'<Registration User:{self.user_id} Event:{self.event_id}>'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=True)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # 'upcoming_event', 'deadline', 'registration_confirmation'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='notifications')
    event = db.relationship('Event', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.notification_type}>'

