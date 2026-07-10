from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    profile = db.relationship('UserProfile', uselist=False, back_populates='user', cascade="all, delete-orphan")
    preferences = db.relationship('UserPreference', uselist=False, back_populates='user', cascade="all, delete-orphan")
    workout_plans = db.relationship('WorkoutPlan', back_populates='user', cascade="all, delete-orphan")
    workout_sessions = db.relationship('WorkoutSession', back_populates='user', cascade="all, delete-orphan")
    progress_records = db.relationship('ProgressRecord', back_populates='user', cascade="all, delete-orphan")
    recommendations = db.relationship('RecommendationHistory', back_populates='user', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Body Metrics & Bio info
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True) # Male, Female, Other
    height = db.Column(db.Float, nullable=True) # in cm
    weight = db.Column(db.Float, nullable=True) # in kg
    
    # Goals and Preferences
    activity_level = db.Column(db.String(50), nullable=True) # Sedentary, Lightly Active, etc.
    fitness_goal = db.Column(db.String(50), nullable=True) # Weight Loss, Muscle Gain, Strength, etc.
    fitness_level = db.Column(db.String(50), nullable=True) # Beginner, Intermediate, Advanced
    workout_experience = db.Column(db.String(50), nullable=True)
    medical_limitations = db.Column(db.Text, nullable=True) # Comma-separated list of muscle groups/injuries
    daily_time_limit = db.Column(db.Integer, default=60) # in minutes
    available_equipment = db.Column(db.Text, nullable=True) # Comma separated: Bodyweight, Dumbbell, Barbell, Cable, Machine, etc.
    preferred_muscles = db.Column(db.Text, nullable=True) # Comma separated
    training_frequency = db.Column(db.Integer, default=3) # days per week
    
    # Calculated Targets
    bmr = db.Column(db.Float, nullable=True) # calories
    tdee = db.Column(db.Float, nullable=True) # calories
    calorie_target = db.Column(db.Float, nullable=True) # calories
    water_target = db.Column(db.Float, default=2500.0) # in ml
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='profile')

    def __repr__(self):
        return f'<UserProfile of User ID {self.user_id}>'
