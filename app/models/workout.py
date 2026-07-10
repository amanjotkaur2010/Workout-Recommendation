from datetime import datetime
from app.models import db

class WorkoutPlan(db.Model):
    __tablename__ = 'workout_plans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    goal = db.Column(db.String(64), nullable=False)
    frequency = db.Column(db.Integer, default=3)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='workout_plans')
    plan_exercises = db.relationship('WorkoutPlanExercise', back_populates='workout_plan', cascade="all, delete-orphan", order_by="WorkoutPlanExercise.day_of_week, WorkoutPlanExercise.order")
    sessions = db.relationship('WorkoutSession', back_populates='workout_plan', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<WorkoutPlan {self.name} for User {self.user_id}>'


class WorkoutPlanExercise(db.Model):
    __tablename__ = 'workout_plan_exercises'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('workout_plans.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    
    day_of_week = db.Column(db.String(20), nullable=False) # e.g. Monday, Wednesday, Friday
    sets = db.Column(db.Integer, nullable=False, default=3)
    reps = db.Column(db.Integer, nullable=False, default=10)
    rest_time = db.Column(db.Integer, nullable=False, default=60) # in seconds
    order = db.Column(db.Integer, nullable=False, default=0) # order of exercises in that day

    # Relationships
    workout_plan = db.relationship('WorkoutPlan', back_populates='plan_exercises')
    exercise = db.relationship('Exercise', back_populates='plan_exercises')

    def __repr__(self):
        return f'<WorkoutPlanExercise Plan {self.plan_id} Exercise {self.exercise_id}>'


class WorkoutSession(db.Model):
    __tablename__ = 'workout_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('workout_plans.id'), nullable=True) # Can be standalone too
    
    date = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Integer, default=0) # in minutes
    calories_burned = db.Column(db.Float, default=0.0)
    is_completed = db.Column(db.Boolean, default=False)
    day_of_week = db.Column(db.String(20), nullable=True) # Day of week label if linked to plan

    # Relationships
    user = db.relationship('User', back_populates='workout_sessions')
    workout_plan = db.relationship('WorkoutPlan', back_populates='sessions')
    logs = db.relationship('WorkoutLog', back_populates='session', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<WorkoutSession ID {self.id} User {self.user_id} Completed {self.is_completed}>'


class WorkoutLog(db.Model):
    __tablename__ = 'workout_logs'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('workout_sessions.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    
    set_number = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, default=0.0) # weight in kg
    reps_completed = db.Column(db.Integer, default=0)
    is_completed = db.Column(db.Boolean, default=True)

    # Relationships
    session = db.relationship('WorkoutSession', back_populates='logs')
    exercise = db.relationship('Exercise', back_populates='logs')

    def __repr__(self):
        return f'<WorkoutLog Set {self.set_number} reps {self.reps_completed} for Session {self.session_id}>'
