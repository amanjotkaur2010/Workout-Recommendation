import sys
from app import create_app
from app.models import db
from app.models.exercise import Exercise, ExerciseCategory

def seed_database():
    app = create_app()
    with app.app_context():
        # Create all tables if they do not exist
        db.create_all()

        print("Seeding Exercise Categories...")
        categories = {
            "Strength": "Exercises targeting muscle building, strength gains, and skeletal support using weights or bodyweight resistance.",
            "Cardio": "Aerobic exercises aimed at increasing heart rate, improving cardiovascular endurance, and burning calories.",
            "Stretching": "Exercises to increase range of motion, improve muscle elasticity, and prevent injury."
        }

        db_categories = {}
        for cat_name, cat_desc in categories.items():
            cat = ExerciseCategory.query.filter_by(name=cat_name).first()
            if not cat:
                cat = ExerciseCategory(name=cat_name, description=cat_desc)
                db.session.add(cat)
                print(f"Added category: {cat_name}")
            else:
                db_categories[cat_name] = cat
        
        db.session.commit()

        # Re-query categories to get correct IDs
        for cat_name in categories:
            db_categories[cat_name] = ExerciseCategory.query.filter_by(name=cat_name).first()

        print("Seeding Exercises...")
        exercises_list = [
            # --- STRENGTH: Chest ---
            {
                "name": "Push-Up",
                "description": "A classic bodyweight exercise targeting the chest, shoulders, and triceps. Keep your core tight and lower your chest to the floor.",
                "category": "Strength",
                "target_muscle": "Chest",
                "secondary_muscles": "Triceps, Shoulders, Abs",
                "difficulty": "Beginner",
                "equipment_required": "Bodyweight",
                "default_sets": 3,
                "default_reps": 12,
                "default_rest_time": 60,
                "calories_per_minute": 5.0,
                "video_url": "https://www.youtube.com/embed/IODxDxX7oi4"
            },
            {
                "name": "Dumbbell Bench Press",
                "description": "Lie flat on a bench holding dumbbells. Press the weights up over your chest, keeping your elbows at a 45-degree angle.",
                "category": "Strength",
                "target_muscle": "Chest",
                "secondary_muscles": "Triceps, Shoulders",
                "difficulty": "Intermediate",
                "equipment_required": "Dumbbell, Bench",
                "default_sets": 4,
                "default_reps": 10,
                "default_rest_time": 90,
                "calories_per_minute": 6.5,
                "video_url": "https://www.youtube.com/embed/VmB1G1K7vTU"
            },
            {
                "name": "Barbell Bench Press",
                "description": "Lying on a bench, lower a barbell to your chest and press it upward. Keep feet flat on the floor and grip wider than shoulder width.",
                "category": "Strength",
                "target_muscle": "Chest",
                "secondary_muscles": "Triceps, Shoulders",
                "difficulty": "Intermediate",
                "equipment_required": "Barbell, Bench",
                "default_sets": 4,
                "default_reps": 8,
                "default_rest_time": 120,
                "calories_per_minute": 7.0,
                "video_url": "https://www.youtube.com/embed/rT7DgCr-3pg"
            },
            {
                "name": "Incline Dumbbell Fly",
                "description": "Lying on an incline bench, hold dumbbells above chest. Lower arms to the sides in a wide arc, maintaining a slight bend in elbows.",
                "category": "Strength",
                "target_muscle": "Chest",
                "secondary_muscles": "Shoulders",
                "difficulty": "Intermediate",
                "equipment_required": "Dumbbell, Bench",
                "default_sets": 3,
                "default_reps": 12,
                "default_rest_time": 90,
                "calories_per_minute": 5.5,
                "video_url": "https://www.youtube.com/embed/ajdF8nXvKzY"
            },

            # --- STRENGTH: Back ---
            {
                "name": "Pull-Up",
                "description": "Grasp a bar with an overhand grip. Pull yourself up until your chin clears the bar, focusing on engaging your latissimus dorsi.",
                "category": "Strength",
                "target_muscle": "Back",
                "secondary_muscles": "Biceps, Shoulders, Forearms",
                "difficulty": "Advanced",
                "equipment_required": "Pull-up Bar",
                "default_sets": 3,
                "default_reps": 8,
                "default_rest_time": 120,
                "calories_per_minute": 8.0,
                "video_url": "https://www.youtube.com/embed/eGo4IYlbE5g"
            },
            {
                "name": "Dumbbell Single-Arm Row",
                "description": "Support your knee and hand on a bench. Hold a dumbbell with your free hand and row it up to your hip.",
                "category": "Strength",
                "target_muscle": "Back",
                "secondary_muscles": "Biceps, Shoulders",
                "difficulty": "Beginner",
                "equipment_required": "Dumbbell, Bench",
                "default_sets": 3,
                "default_reps": 12,
                "default_rest_time": 60,
                "calories_per_minute": 6.0,
                "video_url": "https://www.youtube.com/embed/dFzUjzsS9Bw"
            },
            {
                "name": "Barbell Bent-Over Row",
                "description": "Hinge at your hips, hold a barbell with a medium grip, and pull it to your lower chest, squeezing your shoulder blades together.",
                "category": "Strength",
                "target_muscle": "Back",
                "secondary_muscles": "Biceps, Hamstrings, Lower Back",
                "difficulty": "Intermediate",
                "equipment_required": "Barbell",
                "default_sets": 4,
                "default_reps": 10,
                "default_rest_time": 90,
                "calories_per_minute": 6.8,
                "video_url": "https://www.youtube.com/embed/6FZH1503K0g"
            },
            {
                "name": "Barbell Deadlift",
                "description": "Stand with feet hip-width apart. Hinge at hips and bend knees to grasp the bar. Stand up by extending hips and knees.",
                "category": "Strength",
                "target_muscle": "Back",
                "secondary_muscles": "Hamstrings, Glutes, Lower Back, Forearms",
                "difficulty": "Advanced",
                "equipment_required": "Barbell",
                "default_sets": 4,
                "default_reps": 5,
                "default_rest_time": 180,
                "calories_per_minute": 9.5,
                "video_url": "https://www.youtube.com/embed/op9kVnSso6Q"
            },

            # --- STRENGTH: Legs (Quads, Hamstrings, Glutes, Calves) ---
            {
                "name": "Bodyweight Squat",
                "description": "Stand with feet shoulder-width apart. Lower your hips back and down as if sitting in a chair, keeping chest upright.",
                "category": "Strength",
                "target_muscle": "Quads",
                "secondary_muscles": "Glutes, Hamstrings, Calves",
                "difficulty": "Beginner",
                "equipment_required": "Bodyweight",
                "default_sets": 3,
                "default_reps": 15,
                "default_rest_time": 60,
                "calories_per_minute": 5.0,
                "video_url": "https://www.youtube.com/embed/U3HlEF_E9fo"
            },
            {
                "name": "Dumbbell Goblet Squat",
                "description": "Hold a single dumbbell vertically against your chest. Perform a deep squat, pushing knees outwards.",
                "category": "Strength",
                "target_muscle": "Quads",
                "secondary_muscles": "Glutes, Hamstrings, Calves, Abs",
                "difficulty": "Beginner",
                "equipment_required": "Dumbbell",
                "default_sets": 3,
                "default_reps": 12,
                "default_rest_time": 60,
                "calories_per_minute": 6.0,
                "video_url": "https://www.youtube.com/embed/mGju16pYwU8"
            },
            {
                "name": "Barbell Back Squat",
                "description": "Rest a barbell on your upper traps. Squat down to parallel or below, keeping pressure distributed across your feet.",
                "category": "Strength",
                "target_muscle": "Quads",
                "secondary_muscles": "Glutes, Hamstrings, Lower Back",
                "difficulty": "Intermediate",
                "equipment_required": "Barbell",
                "default_sets": 4,
                "default_reps": 8,
                "default_rest_time": 120,
                "calories_per_minute": 8.0,
                "video_url": "https://www.youtube.com/embed/1oed-UmAxFs"
            },
            {
                "name": "Dumbbell Lunges",
                "description": "Hold dumbbells at your sides. Take a large step forward, bending both knees to 90 degrees. Return and alternate legs.",
                "category": "Strength",
                "target_muscle": "Quads",
                "secondary_muscles": "Glutes, Hamstrings, Calves",
                "difficulty": "Beginner",
                "equipment_required": "Dumbbell",
                "default_sets": 3,
                "default_reps": 10,
                "default_rest_time": 60,
                "calories_per_minute": 5.5,
                "video_url": "https://www.youtube.com/embed/D7KaRcUTQeE"
            },
            {
                "name": "Romanian Deadlift",
                "description": "Hold dumbbells or a barbell. Hinge at hips and lower weights down the front of legs while keeping knees slightly bent and back flat.",
                "category": "Strength",
                "target_muscle": "Hamstrings",
                "secondary_muscles": "Glutes, Lower Back",
                "difficulty": "Intermediate",
                "equipment_required": "Dumbbell",
                "default_sets": 3,
                "default_reps": 10,
                "default_rest_time": 90,
                "calories_per_minute": 6.5,
                "video_url": "https://www.youtube.com/embed/JCXUYuzw01M"
            },
            {
                "name": "Glute Bridge",
                "description": "Lie flat on your back, knees bent, feet flat. Drive hips up, squeezing glutes hard at the top.",
                "category": "Strength",
                "target_muscle": "Glutes",
                "secondary_muscles": "Hamstrings",
                "difficulty": "Beginner",
                "equipment_required": "Bodyweight",
                "default_sets": 3,
                "default_reps": 15,
                "default_rest_time": 60,
                "calories_per_minute": 4.0,
                "video_url": "https://www.youtube.com/embed/8bbE6hySPQY"
            },
            {
                "name": "Calf Raise",
                "description": "Stand on a flat surface or edge of a step. Press through your toes to raise your heels as high as possible.",
                "category": "Strength",
                "target_muscle": "Calves",
                "secondary_muscles": "None",
                "difficulty": "Beginner",
                "equipment_required": "Bodyweight",
                "default_sets": 3,
                "default_reps": 20,
                "default_rest_time": 45,
                "calories_per_minute": 3.0,
                "video_url": "https://www.youtube.com/embed/gwLzBJYoWlU"
            },

            # --- STRENGTH: Shoulders ---
            {
                "name": "Dumbbell Overhead Press",
                "description": "Sit or stand holding dumbbells at shoulder level. Press the weights straight up over your head until arms are extended.",
                "category": "Strength",
                "target_muscle": "Shoulders",
                "secondary_muscles": "Triceps, Chest",
                "difficulty": "Intermediate",
                "equipment_required": "Dumbbell",
                "default_sets": 3,
                "default_reps": 10,
                "default_rest_time": 90,
                "calories_per_minute": 6.0,
                "video_url": "https://www.youtube.com/embed/M2rwvNhTOu0"
            },
            {
                "name": "Dumbbell Lateral Raise",
                "description": "Stand holding dumbbells at your sides. Raise arms outward to shoulder height, maintaining a slight bend at the elbows.",
                "category": "Strength",
                "target_muscle": "Shoulders",
                "secondary_muscles": "None",
                "difficulty": "Beginner",
                "equipment_required": "Dumbbell",
                "default_sets": 3,
                "default_reps": 12,
                "default_rest_time": 60,
                "calories_per_minute": 4.5,
                "video_url": "https://www.youtube.com/embed/WJm8LAePhCo"
            },
            {
                "name": "Barbell Military Press",
                "description": "Stand holding a barbell at collarbone level. Press bar vertically overhead, squeezing glutes and core to keep stable.",
                "category": "Strength",
                "target_muscle": "Shoulders",
                "secondary_muscles": "Triceps, Core",
                "difficulty": "Advanced",
                "equipment_required": "Barbell",
                "default_sets": 4,
                "default_reps": 6,
                "default_rest_time": 120,
                "calories_per_minute": 7.5,
                "video_url": "https://www.youtube.com/embed/2yjwxt_Zy4I"
            },

            # --- STRENGTH: Arms (Biceps, Triceps) ---
            {
                "name": "Dumbbell Bicep Curl",
                "description": "Hold dumbbells with palms forward. Keep elbows close to your torso, and curl weights toward your shoulders.",
                "category": "Strength",
                "target_muscle": "Biceps",
                "secondary_muscles": "Forearms",
                "difficulty": "Beginner",
                "equipment_required": "Dumbbell",
                "default_sets": 3,
                "default_reps": 12,
                "default_rest_time": 60,
                "calories_per_minute": 4.0,
                "video_url": "https://www.youtube.com/embed/yTwoNuq184s"
            },
            {
                "name": "Hammer Curl",
                "description": "Hold dumbbells with palms facing each other (neutral grip). Curl weights, targeting the brachialis muscle.",
                "category": "Strength",
                "target_muscle": "Biceps",
                "secondary_muscles": "Forearms",
                "difficulty": "Beginner",
                "equipment_required": "Dumbbell",
                "default_sets": 3,
                "default_reps": 12,
                "default_rest_time": 60,
                "calories_per_minute": 4.0,
                "video_url": "https://www.youtube.com/embed/OP3w1UP1xwI"
            },
            {
                "name": "Tricep Bench Dips",
                "description": "Position hands on edge of a bench. Extend legs, lower hips by bending elbows, and press back up.",
                "category": "Strength",
                "target_muscle": "Triceps",
                "secondary_muscles": "Shoulders, Chest",
                "difficulty": "Beginner",
                "equipment_required": "Bench",
                "default_sets": 3,
                "default_reps": 12,
                "default_rest_time": 60,
                "calories_per_minute": 4.5,
                "video_url": "https://www.youtube.com/embed/0326dy_-CzM"
            },
            {
                "name": "Overhead Tricep Extension",
                "description": "Hold a dumbbell with both hands overhead. Lower dumbbell behind your head by bending elbows, then press back up.",
                "category": "Strength",
                "target_muscle": "Triceps",
                "secondary_muscles": "Shoulders",
                "difficulty": "Beginner",
                "equipment_required": "Dumbbell",
                "default_sets": 3,
                "default_reps": 12,
                "default_rest_time": 60,
                "calories_per_minute": 4.2,
                "video_url": "https://www.youtube.com/embed/X-iV-CGGBt4"
            },

            # --- STRENGTH: Core / Abs ---
            {
                "name": "Abdominal Crunch",
                "description": "Lie on back with knees bent. Contract abdominals, raising shoulders a few inches off the floor.",
                "category": "Strength",
                "target_muscle": "Abs",
                "secondary_muscles": "None",
                "difficulty": "Beginner",
                "equipment_required": "Bodyweight",
                "default_sets": 3,
                "default_reps": 15,
                "default_rest_time": 45,
                "calories_per_minute": 3.5,
                "video_url": "https://www.youtube.com/embed/Xyd_fa5zoEU"
            },
            {
                "name": "Forearm Plank",
                "description": "Hold your body in a straight line supported by elbows and toes. Squeeze core and glutes hard.",
                "category": "Strength",
                "target_muscle": "Abs",
                "secondary_muscles": "Shoulders, Back, Glutes",
                "difficulty": "Beginner",
                "equipment_required": "Bodyweight",
                "default_sets": 3,
                "default_reps": 60, # 60 seconds
                "default_rest_time": 45,
                "calories_per_minute": 4.5,
                "video_url": "https://www.youtube.com/embed/B296mZDhrP4"
            },
            {
                "name": "Hanging Leg Raise",
                "description": "Hang from a pull-up bar. Keep legs straight and lift them to parallel with the ground, engaging lower abs.",
                "category": "Strength",
                "target_muscle": "Abs",
                "secondary_muscles": "Forearms, Hip Flexors",
                "difficulty": "Advanced",
                "equipment_required": "Pull-up Bar",
                "default_sets": 3,
                "default_reps": 10,
                "default_rest_time": 60,
                "calories_per_minute": 5.0,
                "video_url": "https://www.youtube.com/embed/hdng3Nm1t_g"
            },

            # --- CARDIO ---
            {
                "name": "Jumping Jacks",
                "description": "Jump to a position with legs spread and hands overhead, then return to standard standing position.",
                "category": "Cardio",
                "target_muscle": "Calves",
                "secondary_muscles": "Shoulders, Quads, Glutes",
                "difficulty": "Beginner",
                "equipment_required": "Bodyweight",
                "default_sets": 3,
                "default_reps": 30,
                "default_rest_time": 30,
                "calories_per_minute": 8.0,
                "video_url": "https://www.youtube.com/embed/nGAXJ3_L70E"
            },
            {
                "name": "Mountain Climbers",
                "description": "Get into a plank position. Alternate driving knees into your chest rapidly as if climbing a mountain.",
                "category": "Cardio",
                "target_muscle": "Abs",
                "secondary_muscles": "Shoulders, Chest, Quads",
                "difficulty": "Intermediate",
                "equipment_required": "Bodyweight",
                "default_sets": 3,
                "default_reps": 20,
                "default_rest_time": 45,
                "calories_per_minute": 9.0,
                "video_url": "https://www.youtube.com/embed/zT-9L37GywM"
            },
            {
                "name": "Burpees",
                "description": "Squat down, kick feet back to plank, do a pushup, jump feet forward, and leap explosively into the air.",
                "category": "Cardio",
                "target_muscle": "Quads",
                "secondary_muscles": "Chest, Shoulders, Triceps, Glutes, Abs",
                "difficulty": "Advanced",
                "equipment_required": "Bodyweight",
                "default_sets": 3,
                "default_reps": 10,
                "default_rest_time": 60,
                "calories_per_minute": 11.0,
                "video_url": "https://www.youtube.com/embed/dZgVxmf6jkA"
            },

            # --- STRETCHING ---
            {
                "name": "Cobra Stretch",
                "description": "Lie face down, hands under shoulders. Press through hands to lift chest, stretching abdominals and back.",
                "category": "Stretching",
                "target_muscle": "Abs",
                "secondary_muscles": "Lower Back",
                "difficulty": "Beginner",
                "equipment_required": "Bodyweight",
                "default_sets": 2,
                "default_reps": 30, # 30 seconds hold
                "default_rest_time": 15,
                "calories_per_minute": 2.0,
                "video_url": "https://www.youtube.com/embed/J-05Meyx38s"
            },
            {
                "name": "Child's Pose",
                "description": "Kneel on the floor, sit back on your heels, and reach your arms forward, dropping your forehead to the mat.",
                "category": "Stretching",
                "target_muscle": "Back",
                "secondary_muscles": "Shoulders, Glutes",
                "difficulty": "Beginner",
                "equipment_required": "Bodyweight",
                "default_sets": 2,
                "default_reps": 45, # 45 seconds hold
                "default_rest_time": 15,
                "calories_per_minute": 1.5,
                "video_url": "https://www.youtube.com/embed/U7_P-5n31pQ"
            }
        ]

        for exc_data in exercises_list:
            exc = Exercise.query.filter_by(name=exc_data["name"]).first()
            if not exc:
                cat = db_categories[exc_data["category"]]
                exc = Exercise(
                    name=exc_data["name"],
                    description=exc_data["description"],
                    category_id=cat.id,
                    target_muscle=exc_data["target_muscle"],
                    secondary_muscles=exc_data["secondary_muscles"],
                    difficulty=exc_data["difficulty"],
                    equipment_required=exc_data["equipment_required"],
                    default_sets=exc_data["default_sets"],
                    default_reps=exc_data["default_reps"],
                    default_rest_time=exc_data["default_rest_time"],
                    calories_per_minute=exc_data["calories_per_minute"],
                    video_url=exc_data["video_url"]
                )
                db.session.add(exc)
                print(f"Added exercise: {exc_data['name']}")
                
        db.session.commit()
        print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()
