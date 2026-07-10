from datetime import datetime
from app.models import db

class ProgressRecord(db.Model):
    __tablename__ = 'progress_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow().date, index=True)
    
    # Body stats
    weight = db.Column(db.Float, nullable=True) # in kg
    bmi = db.Column(db.Float, nullable=True)
    body_fat = db.Column(db.Float, nullable=True) # %
    chest = db.Column(db.Float, nullable=True) # in cm
    waist = db.Column(db.Float, nullable=True) # in cm
    arms = db.Column(db.Float, nullable=True) # in cm
    thighs = db.Column(db.Float, nullable=True) # in cm
    
    # Daily logs
    water_intake = db.Column(db.Float, default=0.0) # in ml
    calorie_intake = db.Column(db.Float, default=0.0) # in kcal

    # Relationships
    user = db.relationship('User', back_populates='progress_records')

    def __repr__(self):
        return f'<ProgressRecord User {self.user_id} on {self.date}>'


class UserPreference(db.Model):
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    dark_mode = db.Column(db.Boolean, default=True)
    email_notifications = db.Column(db.Boolean, default=True)
    workout_reminders = db.Column(db.Boolean, default=True)

    # Relationships
    user = db.relationship('User', back_populates='preferences')

    def __repr__(self):
        return f'<UserPreference User {self.user_id}>'


class RecommendationHistory(db.Model):
    __tablename__ = 'recommendation_histories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Snapshots (stored as JSON)
    profile_snapshot = db.Column(db.JSON, nullable=False)
    recommendations_json = db.Column(db.JSON, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='recommendations')

    def __repr__(self):
        return f'<RecommendationHistory User {self.user_id} on {self.date}>'
