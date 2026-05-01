from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    avatar_url = db.Column(db.String(255))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    achievements = db.relationship('Achievement', backref='author', lazy=True, cascade='all, delete-orphan')
    verifications = db.relationship('Verification', backref='verifier', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'created_at': self.created_at.isoformat(),
            'total_points': self.get_total_points(),
            'verified_achievements': len([a for a in self.achievements if a.verified])
        }
    
    def get_total_points(self):
        return sum([a.points for a in self.achievements if a.verified])

class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True)
    difficulty = db.Column(db.String(50), default='medium')
    points = db.Column(db.Integer, default=100)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    verified = db.Column(db.Boolean, default=False, index=True)
    verification_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    verifications = db.relationship('Verification', backref='achievement', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'difficulty': self.difficulty,
            'points': self.points,
            'author': self.author.username,
            'author_id': self.author_id,
            'verified': self.verified,
            'verification_count': self.verification_count,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def is_fully_verified(self):
        return self.verification_count >= 3

class Verification(db.Model):
    __tablename__ = 'verifications'
    
    id = db.Column(db.Integer, primary_key=True)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    verifier_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='pending', index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('achievement_id', 'verifier_id', name='uq_achievement_verifier'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'achievement_id': self.achievement_id,
            'verifier': self.verifier.username,
            'verifier_id': self.verifier_id,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }