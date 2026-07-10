import json
from datetime import datetime, timedelta
from app.models import db
from app.models.exercise import Exercise
from app.models.workout import WorkoutPlan, WorkoutPlanExercise, WorkoutSession, WorkoutLog
from app.models.progress import RecommendationHistory

def parse_comma_separated(text):
    if not text:
        return []
    return [item.strip().lower() for item in text.split(',') if item.strip()]

def get_banned_muscles(medical_limitations):
    """
    Map medical limitations/injuries to target muscle groups to exclude.
    """
    limitations = parse_comma_separated(medical_limitations)
    banned = set()
    
    mapping = {
        'knee': ['quads', 'hamstrings', 'calves'],
        'shoulder': ['shoulders', 'chest', 'back'],
        'back': ['back', 'lower back', 'hamstrings'],
        'lower back': ['back', 'lower back', 'hamstrings'],
        'neck': ['shoulders', 'neck'],
        'wrist': ['forearms', 'biceps', 'triceps', 'chest'],
        'elbow': ['triceps', 'biceps', 'forearms'],
        'ankle': ['calves', 'quads'],
        'hip': ['glutes', 'quads', 'hamstrings']
    }
    
    for lim in limitations:
        for keyword, muscles in mapping.items():
            if keyword in lim:
                banned.update(muscles)
                
    return list(banned)

def generate_recommendation(user_profile):
    """
    Generates a personalized WorkoutPlan and links appropriate Exercises.
    Saves to the database, logs in RecommendationHistory, and returns the new plan.
    """
    user_id = user_profile.user_id
    
    # 1. Parse limitations, equipment, and preferred muscles
    banned_muscles = get_banned_muscles(user_profile.medical_limitations)
    available_equip = parse_comma_separated(user_profile.available_equipment)
    # Always include bodyweight as an available option
    if 'bodyweight' not in available_equip:
        available_equip.append('bodyweight')
        
    preferred_muscles = parse_comma_separated(user_profile.preferred_muscles)
    
    # 2. Query all exercises from the database
    all_exercises = Exercise.query.all()
    
    # 3. Filter exercises
    filtered_exercises = []
    for exc in all_exercises:
        # Check medical limitations
        target_m_lower = exc.target_muscle.lower()
        if target_m_lower in banned_muscles:
            continue
            
        # Check secondary muscles for limitations
        sec_muscles = parse_comma_separated(exc.secondary_muscles)
        if any(m in banned_muscles for m in sec_muscles):
            continue
            
        # Check equipment requirements
        exc_equip = parse_comma_separated(exc.equipment_required)
        # All required equipment for this exercise must be available to the user
        if not all(eq in available_equip for eq in exc_equip):
            continue
            
        # Check difficulty matching
        # Beginner: only Beginner
        # Intermediate: Beginner & Intermediate
        # Advanced: Beginner, Intermediate & Advanced
        exc_diff = exc.difficulty.lower()
        user_level = user_profile.fitness_level.lower() if user_profile.fitness_level else 'beginner'
        
        if user_level == 'beginner' and exc_diff != 'beginner':
            continue
        elif user_level == 'intermediate' and exc_diff not in ['beginner', 'intermediate']:
            continue
            
        filtered_exercises.append(exc)
        
    # If we filtered out too many exercises, fallback to including bodyweight beginner exercises
    if len(filtered_exercises) < 6:
        # Fallback to absolute basics
        filtered_exercises = [exc for exc in all_exercises if exc.difficulty.lower() == 'beginner' and 'bodyweight' in parse_comma_separated(exc.equipment_required)]

    # 4. Define reps, sets, rest, and intensity multiplier based on user goal
    goal = user_profile.fitness_goal
    if goal == 'Muscle Gain':
        sets = 4
        reps = 10
        rest = 90
        rep_range = "8-12 reps"
    elif goal == 'Strength':
        sets = 5
        reps = 5
        rest = 150
        rep_range = "3-6 reps"
    elif goal == 'Endurance':
        sets = 3
        reps = 15
        rest = 45
        rep_range = "15-20 reps"
    elif goal == 'Weight Loss':
        sets = 3
        reps = 12
        rest = 45
        rep_range = "12-15 reps"
    else: # General Fitness / Maintenance
        sets = 3
        reps = 10
        rest = 60
        rep_range = "10-12 reps"

    # 5. Structure the split based on weekly frequency
    frequency = user_profile.training_frequency or 3
    days = []
    if frequency == 1:
        days = ['Wednesday']
    elif frequency == 2:
        days = ['Tuesday', 'Thursday']
    elif frequency == 3:
        days = ['Monday', 'Wednesday', 'Friday']
    elif frequency == 4:
        days = ['Monday', 'Tuesday', 'Thursday', 'Friday']
    elif frequency == 5:
        days = ['Monday', 'Tuesday', 'Wednesday', 'Friday', 'Saturday']
    else:
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][:frequency]

    # Deactivate existing plans for this user
    WorkoutPlan.query.filter_by(user_id=user_id, is_active=True).update({'is_active': False})
    
    # Create new plan
    plan_name = f"AI {goal} Program ({frequency} Days/Week)"
    new_plan = WorkoutPlan(
        user_id=user_id,
        name=plan_name,
        goal=goal,
        frequency=frequency,
        is_active=True
    )
    db.session.add(new_plan)
    db.session.flush() # Populate new_plan.id

    # Group exercises by target muscles to distribute them logically
    muscle_groups = {}
    for exc in filtered_exercises:
        m = exc.target_muscle.lower()
        if m not in muscle_groups:
            muscle_groups[m] = []
        muscle_groups[m].append(exc)

    # Distribute exercises into days based on splits
    # For a Full Body Split (1, 2, 3 days)
    # Each day should contain: 1 Quad/Leg exercise, 1 Chest/Push exercise, 1 Back/Pull exercise, 1 Shoulder exercise, 1 Core/Arm exercise
    # For Upper/Lower Split (4 days)
    # Day 1 & 3: Upper Body (Chest, Back, Shoulders, Arms)
    # Day 2 & 4: Lower Body & Core (Quads, Hamstrings, Glutes, Calves, Abs)
    # For Push/Pull/Legs Split (5 days)
    # Day 1 (Push): Chest, Shoulders, Triceps
    # Day 2 (Pull): Back, Biceps
    # Day 3 (Legs): Quads, Hamstrings, Calves
    # Day 4 (Upper): Chest, Back, Shoulders, Arms
    # Day 5 (Lower/Core): Legs, Abs

    plan_exercises_to_add = []
    
    for idx, day in enumerate(days):
        day_exercises = []
        
        # Decide what muscle groups to target today based on splits
        target_muscles_today = []
        if len(days) <= 3:
            # Full Body split - target all major areas
            target_muscles_today = ['quads', 'chest', 'back', 'shoulders', 'glutes', 'abs', 'biceps', 'triceps', 'hamstrings']
        else:
            # Upper/Lower or PPL split
            if len(days) == 4:
                # 4 Days: Monday(Upper), Tuesday(Lower), Thursday(Upper), Friday(Lower)
                if idx in [0, 2]: # Upper
                    target_muscles_today = ['chest', 'back', 'shoulders', 'biceps', 'triceps']
                else: # Lower
                    target_muscles_today = ['quads', 'hamstrings', 'glutes', 'calves', 'abs']
            elif len(days) == 5:
                # 5 Days: Push, Pull, Legs, Upper, Lower
                if idx == 0: # Push
                    target_muscles_today = ['chest', 'shoulders', 'triceps']
                elif idx == 1: # Pull
                    target_muscles_today = ['back', 'biceps']
                elif idx == 2: # Legs
                    target_muscles_today = ['quads', 'hamstrings', 'glutes', 'calves']
                elif idx == 3: # Upper
                    target_muscles_today = ['chest', 'back', 'shoulders', 'biceps', 'triceps']
                else: # Lower / Core
                    target_muscles_today = ['quads', 'hamstrings', 'glutes', 'abs', 'calves']

        # Pick exercises for today
        # Prioritize preferred muscle groups if they match today's target muscles
        available_targets = [m for m in target_muscles_today if m in muscle_groups and len(muscle_groups[m]) > 0]
        
        # Keep track of selected exercises to avoid duplicates on the same day
        selected_ids_today = set()
        
        # We target about 5 to 7 exercises per session based on daily time limit
        max_exercises = max(4, min(8, int(user_profile.daily_time_limit / 10)))
        
        # Pull exercises from target muscle groups
        count = 0
        # First check preferred muscles
        for pm in preferred_muscles:
            if pm in target_muscles_today and pm in muscle_groups:
                for exc in muscle_groups[pm]:
                    if exc.id not in selected_ids_today and count < max_exercises:
                        day_exercises.append(exc)
                        selected_ids_today.add(exc.id)
                        count += 1
                        break
                        
        # Now fill up with other target muscles
        for m in target_muscles_today:
            if m in muscle_groups:
                # Try to get an exercise
                for exc in muscle_groups[m]:
                    if exc.id not in selected_ids_today and count < max_exercises:
                        day_exercises.append(exc)
                        selected_ids_today.add(exc.id)
                        count += 1
                        break
                        
        # If we still have space and need exercises, pick any available from today's targets
        if count < max_exercises:
            for m in target_muscles_today:
                if m in muscle_groups:
                    for exc in muscle_groups[m]:
                        if exc.id not in selected_ids_today and count < max_exercises:
                            day_exercises.append(exc)
                            selected_ids_today.add(exc.id)
                            count += 1
        
        # Order exercises: compound movements first, then isolation, then abs
        # For simplicity, sort by difficulty and categories
        day_exercises.sort(key=lambda e: (0 if e.target_muscle.lower() in ['quads', 'chest', 'back'] else 1))

        # Add plan exercises to batch
        for order_idx, exc in enumerate(day_exercises):
            # Estimate calories burned based on exercise MET proxy and user weight
            # Calorie burn = default_calories_per_minute * rest_time_adjustment * weight
            weight_factor = (user_profile.weight or 70.0) / 70.0
            est_duration = (sets * (reps * 3 + rest)) / 60.0 # sets * (time per set + rest) in minutes
            est_calories = round(exc.calories_per_minute * est_duration * weight_factor, 1)

            plan_exc = WorkoutPlanExercise(
                plan_id=new_plan.id,
                exercise_id=exc.id,
                day_of_week=day,
                sets=sets,
                reps=reps,
                rest_time=rest,
                order=order_idx
            )
            plan_exercises_to_add.append(plan_exc)

    db.session.add_all(plan_exercises_to_add)
    
    # 6. Save Snapshot in RecommendationHistory
    profile_snapshot = {
        'age': user_profile.age,
        'gender': user_profile.gender,
        'height': user_profile.height,
        'weight': user_profile.weight,
        'fitness_goal': user_profile.fitness_goal,
        'fitness_level': user_profile.fitness_level,
        'available_equipment': user_profile.available_equipment,
        'medical_limitations': user_profile.medical_limitations,
        'training_frequency': user_profile.training_frequency,
        'preferred_muscles': user_profile.preferred_muscles,
        'bmr': user_profile.bmr,
        'tdee': user_profile.tdee,
        'calorie_target': user_profile.calorie_target
    }
    
    recommendation_details = []
    for pe in plan_exercises_to_add:
        # Load exercise name to make snapshot readable
        exc = Exercise.query.get(pe.exercise_id)
        recommendation_details.append({
            'day': pe.day_of_week,
            'exercise': exc.name,
            'sets': pe.sets,
            'reps': pe.reps,
            'rest_time': pe.rest_time,
            'order': pe.order
        })

    rec_history = RecommendationHistory(
        user_id=user_id,
        profile_snapshot=profile_snapshot,
        recommendations_json=recommendation_details
    )
    db.session.add(rec_history)
    db.session.commit()
    
    return new_plan

def suggest_substitution(exercise_id, user_profile):
    """
    Returns up to 3 alternative exercises that target the same primary muscle,
    match user level and equipment, and do not violate medical limitations.
    """
    original = Exercise.query.get(exercise_id)
    if not original:
        return []
        
    banned_muscles = get_banned_muscles(user_profile.medical_limitations)
    available_equip = parse_comma_separated(user_profile.available_equipment)
    if 'bodyweight' not in available_equip:
        available_equip.append('bodyweight')
        
    # Same target muscle, different exercise
    alternatives = Exercise.query.filter(
        Exercise.target_muscle == original.target_muscle,
        Exercise.id != original.id
    ).all()
    
    results = []
    for exc in alternatives:
        target_m_lower = exc.target_muscle.lower()
        if target_m_lower in banned_muscles:
            continue
            
        sec_muscles = parse_comma_separated(exc.secondary_muscles)
        if any(m in banned_muscles for m in sec_muscles):
            continue
            
        exc_equip = parse_comma_separated(exc.equipment_required)
        if not all(eq in available_equip for eq in exc_equip):
            continue
            
        exc_diff = exc.difficulty.lower()
        user_level = user_profile.fitness_level.lower() if user_profile.fitness_level else 'beginner'
        if user_level == 'beginner' and exc_diff != 'beginner':
            continue
        elif user_level == 'intermediate' and exc_diff not in ['beginner', 'intermediate']:
            continue
            
        results.append(exc)
        
    return results[:3]

def check_progression_and_deload(user_id):
    """
    Analyzes user logs to suggest deload periods or weight/rep progressions.
    Returns: dict with 'deload_recommended' (bool), 'deload_reason' (str),
                         'progression_recommendations' (list of dicts)
    """
    result = {
        'deload_recommended': False,
        'deload_reason': '',
        'progression_recommendations': []
    }
    
    # 1. Deload Check
    # Check if user has been logging workout sessions for the last 6 consecutive weeks
    # without a deload week.
    six_weeks_ago = datetime.utcnow() - timedelta(weeks=6)
    recent_sessions = WorkoutSession.query.filter(
        WorkoutSession.user_id == user_id,
        WorkoutSession.date >= six_weeks_ago,
        WorkoutSession.is_completed == True
    ).all()
    
    # Group by week number
    weeks_active = set()
    for s in recent_sessions:
        # Get ISO week number
        weeks_active.add(s.date.isocalendar()[1])
        
    if len(weeks_active) >= 6:
        result['deload_recommended'] = True
        result['deload_reason'] = "You have completed workouts consistently for 6 consecutive weeks. A deload week is recommended to allow joints and nervous system to recover. Suggest reducing workout volume (sets/reps) by 40-50%."

    # 2. Progression Check
    # Check each exercise logged in the last 2 completed sessions.
    # If the user completed all target reps & sets at the same weight, suggest progression.
    # Get last 5 completed workout sessions
    last_sessions = WorkoutSession.query.filter(
        WorkoutSession.user_id == user_id,
        WorkoutSession.is_completed == True
    ).order_by(WorkoutSession.date.desc()).limit(5).all()
    
    if len(last_sessions) >= 2:
        # Map exercise completion logs
        # Find exercises logged in the last 2 sessions
        # For simplicity, look at exercises that appear in these sessions and audit logs
        exercise_logs = {}
        for s in last_sessions:
            for log in s.logs:
                if log.is_completed:
                    if log.exercise_id not in exercise_logs:
                        exercise_logs[log.exercise_id] = []
                    exercise_logs[log.exercise_id].append({
                        'date': s.date,
                        'weight': log.weight,
                        'reps': log.reps_completed,
                        'set': log.set_number
                    })
                    
        # Audit each exercise to see if they completed all sets at target weights/reps twice
        for exc_id, logs in exercise_logs.items():
            # Need at least 2 sessions logged for this exercise
            # Group logs by date
            dates = {}
            for l in logs:
                d_str = l['date'].strftime('%Y-%m-%d')
                if d_str not in dates:
                    dates[d_str] = []
                dates[d_str].append(l)
                
            if len(dates) >= 2:
                # Sort dates descending (most recent first)
                sorted_dates = sorted(list(dates.keys()), reverse=True)[:2]
                session1 = dates[sorted_dates[0]]
                session2 = dates[sorted_dates[1]]
                
                # Check if reps completed match target and weights are same
                # First get the planned sets/reps for this exercise if active
                pe = WorkoutPlanExercise.query.join(WorkoutPlan).filter(
                    WorkoutPlan.user_id == user_id,
                    WorkoutPlan.is_active == True,
                    WorkoutPlanExercise.exercise_id == exc_id
                ).first()
                
                if pe:
                    target_sets = pe.sets
                    target_reps = pe.reps
                    
                    # Check if user successfully logged target sets/reps in session1 and session2
                    s1_ok = len(session1) >= target_sets and all(l['reps'] >= target_reps for l in session1)
                    s2_ok = len(session2) >= target_sets and all(l['reps'] >= target_reps for l in session2)
                    
                    if s1_ok and s2_ok:
                        exc = Exercise.query.get(exc_id)
                        # Ensure we recommend progression based on the weight used
                        avg_weight = sum(l['weight'] for l in session1) / len(session1)
                        rec_weight = round(avg_weight + (2.5 if avg_weight > 0 else 0) or 1.0, 1)
                        
                        if avg_weight > 0:
                            message = f"Increase weight from {avg_weight} kg to {rec_weight} kg (approx 5% increase) for {exc.name}."
                        else:
                            message = f"Increase resistance or add 1-2 reps to each set of {exc.name} (currently bodyweight)."
                            
                        result['progression_recommendations'].append({
                            'exercise_id': exc_id,
                            'exercise_name': exc.name,
                            'current_avg_weight': avg_weight,
                            'recommended_next_step': message
                        })
                        
    return result
