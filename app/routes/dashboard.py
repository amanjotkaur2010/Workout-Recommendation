from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import db
from app.models.user import UserProfile
from app.models.progress import ProgressRecord, UserPreference
from app.models.workout import WorkoutSession
from app.services.calculator import (
    calculate_bmi, calculate_bmr, calculate_tdee,
    calculate_calorie_target, calculate_water_target
)

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    profile = current_user.profile
    if not profile or not profile.age:
        flash('Please fill in your fitness profile first.', 'warning')
        return redirect(url_for('dashboard.profile'))
        
    today = datetime.utcnow().date()
    
    # Get or create today's progress record
    record = ProgressRecord.query.filter_by(user_id=current_user.id, date=today).first()
    if not record:
        record = ProgressRecord(user_id=current_user.id, date=today, weight=profile.weight)
        db.session.add(record)
        db.session.commit()
        
    # Stats Calculations
    # 1. Calories Burned today
    today_sessions = WorkoutSession.query.filter(
        WorkoutSession.user_id == current_user.id,
        WorkoutSession.is_completed == True,
        db.func.date(WorkoutSession.date) == today
    ).all()
    calories_burned = sum(s.calories_burned for s in today_sessions)
    
    # 2. Workout Completion Rate (this week)
    start_of_week = today - timedelta(days=today.weekday()) # Monday
    weekly_sessions = WorkoutSession.query.filter(
        WorkoutSession.user_id == current_user.id,
        WorkoutSession.date >= datetime.combine(start_of_week, datetime.min.time())
    ).all()
    
    completed_this_week = sum(1 for s in weekly_sessions if s.is_completed)
    total_this_week = len(weekly_sessions)
    completion_rate = int((completed_this_week / total_this_week * 100)) if total_this_week > 0 else 0
    
    # 3. Workout Streak (consecutive days with completed workout sessions)
    streak = 0
    check_date = today
    while True:
        session_exists = WorkoutSession.query.filter(
            WorkoutSession.user_id == current_user.id,
            WorkoutSession.is_completed == True,
            db.func.date(WorkoutSession.date) == check_date
        ).first()
        if session_exists:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            # Check if they just missed today but got yesterday, they might still be on a streak
            if check_date == today:
                check_date -= timedelta(days=1)
                continue
            break
            
    # 4. Fitness Score (Calculated metric out of 100 based on BMI category, goal completion, water, and calorie targets)
    fitness_score = 50 # Base
    bmi, bmi_cat = calculate_bmi(profile.weight, profile.height)
    if bmi_cat == 'Normal':
        fitness_score += 15
    elif bmi_cat in ['Underweight', 'Overweight']:
        fitness_score += 5
        
    # Water & Calorie target compliance
    if record.water_intake >= (profile.water_target or 2500):
        fitness_score += 15
    elif record.water_intake >= (profile.water_target or 2500) * 0.5:
        fitness_score += 5
        
    cal_diff = abs(record.calorie_intake - (profile.calorie_target or 2000))
    if cal_diff < 200:
        fitness_score += 20
    elif cal_diff < 500:
        fitness_score += 10
        
    # Workout streak bonus
    fitness_score += min(10, streak * 2)
    fitness_score = min(100, fitness_score)
    
    # Recent workouts
    recent_workouts = WorkoutSession.query.filter_by(user_id=current_user.id).order_by(WorkoutSession.date.desc()).limit(5).all()
    
    return render_template('dashboard/index.html',
                           profile=profile,
                           record=record,
                           calories_burned=calories_burned,
                           completion_rate=completion_rate,
                           streak=streak,
                           fitness_score=fitness_score,
                           recent_workouts=recent_workouts)


@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile = current_user.profile
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
        
    if request.method == 'POST':
        # Retrieve form data
        profile.age = request.form.get('age', type=int)
        profile.gender = request.form.get('gender')
        profile.height = request.form.get('height', type=float)
        profile.weight = request.form.get('weight', type=float)
        profile.activity_level = request.form.get('activity_level')
        profile.fitness_goal = request.form.get('fitness_goal')
        profile.fitness_level = request.form.get('fitness_level')
        profile.workout_experience = request.form.get('workout_experience')
        profile.medical_limitations = request.form.get('medical_limitations', '')
        profile.daily_time_limit = request.form.get('daily_time_limit', type=int) or 60
        profile.training_frequency = request.form.get('training_frequency', type=int) or 3
        
        # Parse multi-select items
        available_equip = request.form.getlist('available_equipment')
        profile.available_equipment = ', '.join(available_equip)
        
        preferred_muscles = request.form.getlist('preferred_muscles')
        profile.preferred_muscles = ', '.join(preferred_muscles)
        
        # Calculate BMR, TDEE, Calorie and Water targets
        if profile.weight and profile.height and profile.age:
            profile.bmr = calculate_bmr(profile.weight, profile.height, profile.age, profile.gender)
            profile.tdee = calculate_tdee(profile.bmr, profile.activity_level)
            profile.calorie_target = calculate_calorie_target(profile.tdee, profile.fitness_goal)
            profile.water_target = calculate_water_target(profile.weight, profile.activity_level)
            
            # Update today's Progress Record weight if it exists
            today_record = ProgressRecord.query.filter_by(user_id=current_user.id, date=datetime.utcnow().date()).first()
            if today_record:
                today_record.weight = profile.weight
                today_record.bmi, _ = calculate_bmi(profile.weight, profile.height)
            else:
                bmi, _ = calculate_bmi(profile.weight, profile.height)
                today_record = ProgressRecord(
                    user_id=current_user.id,
                    date=datetime.utcnow().date(),
                    weight=profile.weight,
                    bmi=bmi
                )
                db.session.add(today_record)
        
        db.session.commit()
        flash('Profile and fitness goals updated successfully!', 'success')
        return redirect(url_for('dashboard.index'))
        
    return render_template('dashboard/profile.html', profile=profile)


@dashboard_bp.route('/log-water', methods=['POST'])
@login_required
def log_water():
    amount = request.form.get('amount', type=float) or 0.0
    today = datetime.utcnow().date()
    
    record = ProgressRecord.query.filter_by(user_id=current_user.id, date=today).first()
    if not record:
        record = ProgressRecord(user_id=current_user.id, date=today, weight=current_user.profile.weight if current_user.profile else None)
        db.session.add(record)
        
    record.water_intake += amount
    db.session.commit()
    flash(f"Logged {int(amount)} ml of water.", 'success')
    return redirect(url_for('dashboard.index'))


@dashboard_bp.route('/log-calories', methods=['POST'])
@login_required
def log_calories():
    amount = request.form.get('amount', type=float) or 0.0
    today = datetime.utcnow().date()
    
    record = ProgressRecord.query.filter_by(user_id=current_user.id, date=today).first()
    if not record:
        record = ProgressRecord(user_id=current_user.id, date=today, weight=current_user.profile.weight if current_user.profile else None)
        db.session.add(record)
        
    record.calorie_intake += amount
    db.session.commit()
    flash(f"Logged {int(amount)} kcal consumed.", 'success')
    return redirect(url_for('dashboard.index'))


@dashboard_bp.route('/log-weight', methods=['POST'])
@login_required
def log_weight():
    weight = request.form.get('weight', type=float)
    if not weight or weight <= 0:
        flash("Please enter a valid weight.", 'danger')
        return redirect(url_for('dashboard.index'))
        
    today = datetime.utcnow().date()
    record = ProgressRecord.query.filter_by(user_id=current_user.id, date=today).first()
    if not record:
        record = ProgressRecord(user_id=current_user.id, date=today)
        db.session.add(record)
        
    record.weight = weight
    
    # Also update profile weight
    if current_user.profile:
        current_user.profile.weight = weight
        # Recalculate BMI, BMR, TDEE, targets
        p = current_user.profile
        record.bmi, _ = calculate_bmi(weight, p.height)
        if p.height and p.age:
            p.bmr = calculate_bmr(weight, p.height, p.age, p.gender)
            p.tdee = calculate_tdee(p.bmr, p.activity_level)
            p.calorie_target = calculate_calorie_target(p.tdee, p.fitness_goal)
            p.water_target = calculate_water_target(weight, p.activity_level)
            
    db.session.commit()
    flash(f"Logged weight of {weight} kg.", 'success')
    return redirect(url_for('dashboard.index'))


@dashboard_bp.route('/chart-data')
@login_required
def chart_data():
    # Fetch last 7 progress records
    records = ProgressRecord.query.filter_by(user_id=current_user.id).order_by(ProgressRecord.date.desc()).limit(7).all()
    records.reverse() # chronologically ascending
    
    labels = [r.date.strftime('%a') for r in records] # Days of the week (e.g. Mon, Tue)
    weight_data = [r.weight or 0.0 for r in records]
    water_data = [r.water_intake for r in records]
    calorie_data = [r.calorie_intake for r in records]
    
    calorie_target = current_user.profile.calorie_target if current_user.profile else 2000.0
    water_target = current_user.profile.water_target if current_user.profile else 2500.0
    
    return jsonify({
        'labels': labels,
        'weight': weight_data,
        'water': water_data,
        'calories': calorie_data,
        'calorie_target': calorie_target,
        'water_target': water_target
    })


@dashboard_bp.route('/toggle-theme', methods=['POST'])
@login_required
def toggle_theme():
    # Helper to toggle theme from client side
    pref = current_user.preferences
    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.session.add(pref)
        
    pref.dark_mode = not pref.dark_mode
    db.session.commit()
    return jsonify({'success': True, 'dark_mode': pref.dark_mode})
