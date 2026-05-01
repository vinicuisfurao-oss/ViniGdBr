from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, User, Achievement, Verification
from datetime import datetime
import os

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///denoument.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app)

with app.app_context():
    db.create_all()

# ==================== USERS ENDPOINTS ====================

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users with their stats"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user profile and achievements"""
    user = User.query.get_or_404(user_id)
    user_data = user.to_dict()
    user_data['achievements'] = [a.to_dict() for a in user.achievements]
    return jsonify(user_data)

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.json
    
    if not data.get('username') or not data.get('email'):
        return jsonify({'error': 'Username and email required'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        avatar_url=data.get('avatar_url'),
        bio=data.get('bio')
    )
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except:
        db.session.rollback()
        return jsonify({'error': 'User already exists'}), 409

# ==================== ACHIEVEMENTS ENDPOINTS ====================

@app.route('/api/achievements', methods=['GET'])
def get_achievements():
    """Get all achievements, optionally filtered"""
    category = request.args.get('category')
    verified = request.args.get('verified', type=bool)
    sort = request.args.get('sort', 'points')
    
    query = Achievement.query
    
    if category:
        query = query.filter_by(category=category)
    if verified is not None:
        query = query.filter_by(verified=verified)
    
    if sort == 'points':
        query = query.order_by(Achievement.points.desc())
    elif sort == 'recent':
        query = query.order_by(Achievement.created_at.desc())
    elif sort == 'verified':
        query = query.order_by(Achievement.verification_count.desc())
    
    achievements = query.all()
    return jsonify([a.to_dict() for a in achievements])

@app.route('/api/achievements/<int:achievement_id>', methods=['GET'])
def get_achievement(achievement_id):
    """Get achievement details with verifications"""
    achievement = Achievement.query.get_or_404(achievement_id)
    data = achievement.to_dict()
    data['verifications'] = [v.to_dict() for v in achievement.verifications]
    return jsonify(data)

@app.route('/api/achievements', methods=['POST'])
def create_achievement():
    """Create a new achievement"""
    data = request.json
    
    required = ['title', 'description', 'category', 'author_id']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    achievement = Achievement(
        title=data['title'],
        description=data['description'],
        category=data['category'],
        difficulty=data.get('difficulty', 'medium'),
        points=data.get('points', 100),
        author_id=data['author_id'],
        completed_at=datetime.utcnow()
    )
    
    db.session.add(achievement)
    db.session.commit()
    return jsonify(achievement.to_dict()), 201

@app.route('/api/achievements/<int:achievement_id>', methods=['PUT'])
def update_achievement(achievement_id):
    """Update achievement"""
    achievement = Achievement.query.get_or_404(achievement_id)
    data = request.json
    
    if 'title' in data:
        achievement.title = data['title']
    if 'description' in data:
        achievement.description = data['description']
    if 'category' in data:
        achievement.category = data['category']
    if 'difficulty' in data:
        achievement.difficulty = data['difficulty']
    if 'points' in data:
        achievement.points = data['points']
    
    db.session.commit()
    return jsonify(achievement.to_dict())

# ==================== RANKINGS ENDPOINTS ====================

@app.route('/api/rankings', methods=['GET'])
def get_rankings():
    """Get global rankings by total points"""
    users = User.query.all()
    rankings = [(user, user.get_total_points()) for user in users]
    rankings.sort(key=lambda x: x[1], reverse=True)
    
    return jsonify([
        {
            'rank': idx + 1,
            **user.to_dict(),
            'total_points': points
        }
        for idx, (user, points) in enumerate(rankings)
    ])

@app.route('/api/rankings/category/<category>', methods=['GET'])
def get_category_rankings(category):
    """Get rankings for a specific category"""
    achievements = Achievement.query.filter_by(category=category, verified=True).all()
    user_points = {}
    
    for achievement in achievements:
        user_id = achievement.author_id
        user_points[user_id] = user_points.get(user_id, 0) + achievement.points
    
    rankings = [(User.query.get(uid), points) for uid, points in user_points.items()]
    rankings.sort(key=lambda x: x[1], reverse=True)
    
    return jsonify([
        {
            'rank': idx + 1,
            'user': user.to_dict(),
            'category_points': points
        }
        for idx, (user, points) in enumerate(rankings)
    ])

# ==================== VERIFICATION ENDPOINTS ====================

@app.route('/api/verifications', methods=['POST'])
def create_verification():
    """Submit verification for an achievement"""
    data = request.json
    
    if not data.get('achievement_id') or not data.get('verifier_id'):
        return jsonify({'error': 'achievement_id and verifier_id required'}), 400
    
    # Check if verification already exists
    existing = Verification.query.filter_by(
        achievement_id=data['achievement_id'],
        verifier_id=data['verifier_id']
    ).first()
    
    if existing:
        return jsonify({'error': 'Already verified by this user'}), 409
    
    verification = Verification(
        achievement_id=data['achievement_id'],
        verifier_id=data['verifier_id'],
        status='approved',
        notes=data.get('notes')
    )
    
    db.session.add(verification)
    db.session.commit()
    
    # Check if achievement should be marked as verified (3+ approvals)
    achievement = Achievement.query.get(data['achievement_id'])
    achievement.verification_count = len(achievement.verifications)
    
    if achievement.verification_count >= 3:
        achievement.verified = True
    
    db.session.commit()
    
    return jsonify(verification.to_dict()), 201

@app.route('/api/verifications/<int:achievement_id>', methods=['GET'])
def get_achievement_verifications(achievement_id):
    """Get all verifications for an achievement"""
    achievement = Achievement.query.get_or_404(achievement_id)
    return jsonify([v.to_dict() for v in achievement.verifications])

# ==================== UTILITY ENDPOINTS ====================

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all achievement categories"""
    categories = db.session.query(Achievement.category).distinct().all()
    return jsonify([cat[0] for cat in categories])

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)