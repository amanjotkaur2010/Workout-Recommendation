from app.models import db

class ExerciseCategory(db.Model):
    __tablename__ = 'exercise_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Relationships
    exercises = db.relationship('Exercise', back_populates='category', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<ExerciseCategory {self.name}>'


class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('exercise_categories.id'), nullable=False)
    
    target_muscle = db.Column(db.String(64), nullable=False) # e.g. Chest, Quads, Hamstrings, Back, Shoulders, Biceps, Triceps, Abs, Calves
    secondary_muscles = db.Column(db.Text, nullable=True) # Comma-separated list
    difficulty = db.Column(db.String(32), nullable=False) # Beginner, Intermediate, Advanced
    equipment_required = db.Column(db.String(128), nullable=False) # Comma-separated list of required equipment (e.g. Bodyweight, Dumbbell, Barbell, Cable, Machine)
    
    # Defaults for generating recommendations
    default_sets = db.Column(db.Integer, default=3)
    default_reps = db.Column(db.Integer, default=10)
    default_rest_time = db.Column(db.Integer, default=60) # in seconds
    calories_per_minute = db.Column(db.Float, default=6.0) # standard calories burned estimate
    
    video_url = db.Column(db.String(256), nullable=True) # URL to instructional video
    image_url = db.Column(db.String(256), nullable=True)

    # Relationships
    category = db.relationship('ExerciseCategory', back_populates='exercises')
    plan_exercises = db.relationship('WorkoutPlanExercise', back_populates='exercise', cascade="all, delete-orphan")
    logs = db.relationship('WorkoutLog', back_populates='exercise', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Exercise {self.name}>'
