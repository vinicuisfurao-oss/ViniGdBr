# 🏆 Denoument List

A Pointercrate-inspired achievement ranking and leaderboard system. Track, verify, and celebrate completed milestones and resolved challenges.

## 📋 Features

- **🎯 Achievement Tracking** - Submit and track completed achievements
- **🏅 Leaderboards** - Global and category-specific rankings
- **✅ Verification System** - Multi-user verification with 3-approval threshold
- **📊 Detailed Stats** - Track points, verification counts, and user profiles
- **🔍 Search & Filter** - Find achievements and users easily
- **🎨 Modern UI** - Beautiful, responsive web interface

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL or SQLite
- Node.js (optional, for frontend bundling)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Set database URL (optional, defaults to SQLite)
export DATABASE_URL="sqlite:///denoument.db"

# Run Flask app
python app.py
```

API will be available at `http://localhost:5000/api`

### Frontend Setup

```bash
cd frontend
# Serve with any HTTP server
python -m http.server 8000
```

Open `http://localhost:8000` in your browser.

## 📚 API Endpoints

### Users
- `GET /api/users` - Get all users
- `GET /api/users/<id>` - Get user details
- `POST /api/users` - Create new user

### Achievements
- `GET /api/achievements` - List achievements (filterable)
- `GET /api/achievements/<id>` - Get achievement details
- `POST /api/achievements` - Create achievement
- `PUT /api/achievements/<id>` - Update achievement

### Rankings
- `GET /api/rankings` - Global rankings
- `GET /api/rankings/category/<category>` - Category rankings

### Verification
- `POST /api/verifications` - Submit verification
- `GET /api/verifications/<achievement_id>` - Get achievement verifications

### Utility
- `GET /api/categories` - Get all categories
- `GET /api/health` - Health check

## 📊 Achievement Verification Flow

1. User submits achievement
2. Community members verify the achievement
3. Once 3+ approvals are received, achievement becomes verified
4. Verified achievements count toward user's total points

## 🎯 Difficulty Levels

- **Easy** - 50 points
- **Medium** - 100 points (default)
- **Hard** - 250 points
- **Extreme** - 500 points

## 📝 Example Request

```bash
curl -X POST http://localhost:5000/api/achievements \
  -H "Content-Type: application/json" \
  -d '{
    "title": "First 100k Points",
    "description": "Reached 100,000 points in Geometry Dash",
    "category": "Gaming",
    "difficulty": "hard",
    "points": 250,
    "author_id": 1
  }'
```

## 🤝 Contributing

Feel free to submit issues and pull requests!

## 📄 License

MIT License - feel free to use this project however you'd like!