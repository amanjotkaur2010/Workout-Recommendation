from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from app.models import db
from app.models.workout import WorkoutPlan, WorkoutPlanExercise, WorkoutSession, WorkoutLog
from app.models.exercise import Exercise
from app.services.recommender import (
    generate_recommendation, suggest_substitution, check_progression_and_deload
)
from app.services.pdf_generator import generate_workout_pdf

workouts_bp = Blueprint('workouts', __name__)

@workouts_bp.route('/recommend', methods=['GET', 'POST'])
@login_required
def recommend():
    profile = current_user.profile
    if not profile or not profile.age:
        flash('Please set up your profile and metrics first.', 'warning')
        return redirect(url_for('dashboard.profile'))
        
    active_plan = WorkoutPlan.query.filter_by(user_id=current_user.id, is_active=True).first()
    
    if request.method == 'POST':
        try:
            new_plan = generate_recommendation(profile)
            flash(f"New workout program '{new_plan.name}' generated successfully!", 'success')
            return redirect(url_for('workouts.planner'))
        except Exception as e:
            flash(f"Error generating recommendation: {str(e)}", 'danger')
            
    return render_template('workouts/recommend.html', active_plan=active_plan)


@workouts_bp.route('/planner')
@login_required
def planner():
    active_plan = WorkoutPlan.query.filter_by(user_id=current_user.id, is_active=True).first()
    
    # Check deload/progression
    progression_info = check_progression_and_deload(current_user.id)
    
    # Group plan exercises by day of the week
    weekly_schedule = {}
    if active_plan:
        for pe in active_plan.plan_exercises:
            day = pe.day_of_week
            if day not in weekly_schedule:
                weekly_schedule[day] = []
            weekly_schedule[day].append(pe)
            
    # Sort order of days logically
    day_order = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7}
    sorted_days = sorted(list(weekly_schedule.keys()), key=lambda d: day_order.get(d, 8))
    
    return render_template('workouts/planner.html',
                           active_plan=active_plan,
                           weekly_schedule=weekly_schedule,
                           sorted_days=sorted_days,
                           progression=progression_info)


@workouts_bp.route('/substitute/<int:pe_id>', methods=['GET', 'POST'])
@login_required
def substitute(pe_id):
    pe = WorkoutPlanExercise.query.get_or_404(pe_id)
    # Ensure it belongs to current user
    if pe.workout_plan.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('workouts.planner'))
        
    alternatives = suggest_substitution(pe.exercise_id, current_user.profile)
    
    if request.method == 'POST':
        alt_id = request.form.get('alternative_id', type=int)
        if alt_id:
            alt_exc = Exercise.query.get(alt_id)
            if alt_exc:
                pe.exercise_id = alt_exc.id
                db.session.commit()
                flash(f"Substituted '{pe.exercise.name}' with '{alt_exc.name}'.", 'success')
                return redirect(url_for('workouts.planner'))
                
    return render_template('workouts/substitute.html', pe=pe, alternatives=alternatives)


@workouts_bp.route('/log-session/<day_of_week>', methods=['GET', 'POST'])
@login_required
def log_session(day_of_week):
    active_plan = WorkoutPlan.query.filter_by(user_id=current_user.id, is_active=True).first()
    if not active_plan:
        flash('No active workout plan found. Generate one first.', 'warning')
        return redirect(url_for('workouts.recommend'))
        
    # Get exercises for this day of week
    plan_exercises = WorkoutPlanExercise.query.filter_by(plan_id=active_plan.id, day_of_week=day_of_week).order_by(WorkoutPlanExercise.order).all()
    
    if not plan_exercises:
        flash(f'No exercises scheduled for {day_of_week} in your active plan.', 'warning')
        return redirect(url_for('workouts.planner'))
        
    if request.method == 'POST':
        duration = request.form.get('duration', type=int) or 45
        
        # Create WorkoutSession
        session = WorkoutSession(
            user_id=current_user.id,
            plan_id=active_plan.id,
            date=datetime.utcnow(),
            duration=duration,
            is_completed=True,
            day_of_week=day_of_week
        )
        db.session.add(session)
        db.session.flush() # Populate session.id
        
        total_calories_burned = 0.0
        
        # Process logs from form fields
        for pe in plan_exercises:
            exc_id = pe.exercise_id
            exc = pe.exercise
            
            # Loop through set count
            completed_sets = 0
            for s_num in range(1, pe.sets + 1):
                weight_val = request.form.get(f'weight_{exc_id}_{s_num}', type=float) or 0.0
                reps_val = request.form.get(f'reps_{exc_id}_{s_num}', type=int) or 0
                completed = request.form.get(f'completed_{exc_id}_{s_num}') == 'on'
                
                if completed:
                    log = WorkoutLog(
                        session_id=session.id,
                        exercise_id=exc_id,
                        set_number=s_num,
                        weight=weight_val,
                        reps_completed=reps_val,
                        is_completed=True
                    )
                    db.session.add(log)
                    completed_sets += 1
                    
            if completed_sets > 0:
                # Estimate calorie burn: MET proxy per minute * duration fraction for this exercise
                # Fraction of total duration = 1 / total exercises
                frac_duration = duration / len(plan_exercises)
                weight_factor = (current_user.profile.weight or 70.0) / 70.0
                total_calories_burned += (exc.calories_per_minute * frac_duration * weight_factor)
                
        session.calories_burned = round(total_calories_burned, 1)
        db.session.commit()
        flash('Workout session logged successfully! Keep up the good work.', 'success')
        return redirect(url_for('dashboard.index'))
        
    return render_template('workouts/log_session.html', day_of_week=day_of_week, plan_exercises=plan_exercises)


@workouts_bp.route('/history')
@login_required
def history():
    sessions = WorkoutSession.query.filter_by(user_id=current_user.id).order_by(WorkoutSession.date.desc()).all()
    return render_template('workouts/history.html', sessions=sessions)


@workouts_bp.route('/sessions/<int:session_id>')
@login_required
def session_detail(session_id):
    session = WorkoutSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('workouts.history'))
        
    # Group logs by exercise
    exercise_logs = {}
    for log in session.logs:
        exc = log.exercise
        if exc not in exercise_logs:
            exercise_logs[exc] = []
        exercise_logs[exc].append(log)
        
    return render_template('workouts/session_detail.html', session=session, exercise_logs=exercise_logs)


@workouts_bp.route('/planner/pdf')
@login_required
def export_pdf():
    active_plan = WorkoutPlan.query.filter_by(user_id=current_user.id, is_active=True).first()
    if not active_plan:
        flash('No active workout plan found to export.', 'warning')
        return redirect(url_for('workouts.planner'))
        
    try:
        pdf_buffer = generate_workout_pdf(current_user, active_plan)
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"{current_user.username}_workout_plan.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(f"Error exporting PDF: {str(e)}", 'danger')
        return redirect(url_for('workouts.planner'))
