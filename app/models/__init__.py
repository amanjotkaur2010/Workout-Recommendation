from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models here to make them accessible and ensure they are registered with SQLAlchemy
from app.models.user import User, UserProfile
from app.models.exercise import Exercise, ExerciseCategory
from app.models.workout import WorkoutPlan, WorkoutPlanExercise, WorkoutSession, WorkoutLog
from app.models.progress import ProgressRecord, UserPreference, RecommendationHistory
