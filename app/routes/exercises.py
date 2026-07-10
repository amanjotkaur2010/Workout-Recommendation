from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import db
from app.models.exercise import Exercise, ExerciseCategory
from app.services.recommender import suggest_substitution

exercises_bp = Blueprint('exercises', __name__)

@exercises_bp.route('/')
def list_exercises():
    # Fetch filter options
    categories = ExerciseCategory.query.all()
    # Unique target muscles
    muscles_query = db.session.query(Exercise.target_muscle).distinct().all()
    target_muscles = sorted([m[0] for m in muscles_query])
    
    # Query parameters
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category', '')
    muscle = request.args.get('muscle', '')
    difficulty = request.args.get('difficulty', '')
    equipment = request.args.get('equipment', '')
    
    page = request.args.get('page', 1, type=int)
    
    # Base query
    query = Exercise.query
    
    # Apply filters
    if search:
        query = query.filter(Exercise.name.ilike(f'%{search}%') | Exercise.description.ilike(f'%{search}%'))
    if category_id:
        query = query.filter_by(category_id=int(category_id))
    if muscle:
        query = query.filter_by(target_muscle=muscle)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if equipment:
        query = query.filter(Exercise.equipment_required.ilike(f'%{equipment}%'))
        
    pagination = query.order_by(Exercise.name).paginate(page=page, per_page=12, error_out=False)
    exercises = pagination.items
    
    return render_template('exercises/list.html',
                           exercises=exercises,
                           pagination=pagination,
                           categories=categories,
                           target_muscles=target_muscles,
                           search=search,
                           selected_category=category_id,
                           selected_muscle=muscle,
                           selected_difficulty=difficulty,
                           selected_equipment=equipment)


@exercises_bp.route('/<int:exercise_id>')
def detail(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Fetch suggestions if user has set up a profile
    substitutions = []
    if current_user.is_authenticated and current_user.profile and current_user.profile.age:
        substitutions = suggest_substitution(exercise.id, current_user.profile)
        
    return render_template('exercises/detail.html', exercise=exercise, substitutions=substitutions)
