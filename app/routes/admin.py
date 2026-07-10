from functools import wraps
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import db
from app.models.user import User
from app.models.exercise import Exercise, ExerciseCategory
from app.models.workout import WorkoutPlan, WorkoutSession

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def index():
    # Admin stats
    user_count = User.query.count()
    exercise_count = Exercise.query.count()
    active_plans = WorkoutPlan.query.filter_by(is_active=True).count()
    completed_workouts = WorkoutSession.query.filter_by(is_completed=True).count()
    
    # Recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                           user_count=user_count,
                           exercise_count=exercise_count,
                           active_plans=active_plans,
                           completed_workouts=completed_workouts,
                           recent_users=recent_users)


@admin_bp.route('/users')
@login_required
@admin_required
def users_list():
    users = User.query.order_by(User.id).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot remove admin permissions from yourself.', 'danger')
        return redirect(url_for('admin.users_list'))
        
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f"Updated admin status for {user.username}.", 'success')
    return redirect(url_for('admin.users_list'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account from here.', 'danger')
        return redirect(url_for('admin.users_list'))
        
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.username} deleted.", 'success')
    return redirect(url_for('admin.users_list'))


@admin_bp.route('/exercises', methods=['GET', 'POST'])
@login_required
@admin_required
def exercises_list():
    categories = ExerciseCategory.query.all()
    exercises = Exercise.query.order_by(Exercise.name).all()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id')
        target_muscle = request.form.get('target_muscle', '').strip()
        secondary_muscles = request.form.get('secondary_muscles', '').strip()
        difficulty = request.form.get('difficulty')
        equipment_required = request.form.get('equipment_required', '').strip()
        default_sets = request.form.get('default_sets', type=int)
        default_reps = request.form.get('default_reps', type=int)
        default_rest_time = request.form.get('default_rest_time', type=int)
        calories_per_minute = request.form.get('calories_per_minute', type=float)
        video_url = request.form.get('video_url', '').strip()
        
        # Validations
        if not name or not category_id or not target_muscle or not difficulty or not equipment_required:
            flash('Please enter all required fields.', 'danger')
            return redirect(url_for('admin.exercises_list'))
            
        existing = Exercise.query.filter_by(name=name).first()
        if existing:
            flash(f'An exercise named "{name}" already exists.', 'danger')
            return redirect(url_for('admin.exercises_list'))
            
        # Create
        new_exercise = Exercise(
            name=name,
            description=description,
            category_id=int(category_id),
            target_muscle=target_muscle,
            secondary_muscles=secondary_muscles,
            difficulty=difficulty,
            equipment_required=equipment_required,
            default_sets=default_sets or 3,
            default_reps=default_reps or 10,
            default_rest_time=default_rest_time or 60,
            calories_per_minute=calories_per_minute or 6.0,
            video_url=video_url
        )
        db.session.add(new_exercise)
        db.session.commit()
        flash(f'Exercise "{name}" added successfully.', 'success')
        return redirect(url_for('admin.exercises_list'))
        
    return render_template('admin/exercises.html', exercises=exercises, categories=categories)


@admin_bp.route('/exercises/<int:exercise_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_exercise(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    categories = ExerciseCategory.query.all()
    
    if request.method == 'POST':
        exercise.name = request.form.get('name', '').strip()
        exercise.description = request.form.get('description', '').strip()
        exercise.category_id = int(request.form.get('category_id'))
        exercise.target_muscle = request.form.get('target_muscle', '').strip()
        exercise.secondary_muscles = request.form.get('secondary_muscles', '').strip()
        exercise.difficulty = request.form.get('difficulty')
        exercise.equipment_required = request.form.get('equipment_required', '').strip()
        exercise.default_sets = request.form.get('default_sets', type=int) or 3
        exercise.default_reps = request.form.get('default_reps', type=int) or 10
        exercise.default_rest_time = request.form.get('default_rest_time', type=int) or 60
        exercise.calories_per_minute = request.form.get('calories_per_minute', type=float) or 6.0
        exercise.video_url = request.form.get('video_url', '').strip()
        
        # Validations
        if not exercise.name or not exercise.target_muscle or not exercise.difficulty or not exercise.equipment_required:
            flash('Required fields cannot be blank.', 'danger')
            return render_template('admin/edit_exercise.html', exercise=exercise, categories=categories)
            
        # Check duplicate name
        existing = Exercise.query.filter(Exercise.name == exercise.name, Exercise.id != exercise.id).first()
        if existing:
            flash(f'An exercise named "{exercise.name}" already exists.', 'danger')
            return render_template('admin/edit_exercise.html', exercise=exercise, categories=categories)
            
        db.session.commit()
        flash(f'Exercise "{exercise.name}" updated successfully.', 'success')
        return redirect(url_for('admin.exercises_list'))
        
    return render_template('admin/edit_exercise.html', exercise=exercise, categories=categories)


@admin_bp.route('/exercises/<int:exercise_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_exercise(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    db.session.delete(exercise)
    db.session.commit()
    flash(f'Exercise "{exercise.name}" deleted.', 'success')
    return redirect(url_for('admin.exercises_list'))
