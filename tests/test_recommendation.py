import unittest
from app import create_app
from app.config import Config
from app.models import db
from app.models.user import User, UserProfile
from app.models.exercise import Exercise, ExerciseCategory
from app.services.calculator import calculate_bmi, calculate_bmr, calculate_tdee, calculate_calorie_target
from app.services.recommender import generate_recommendation, get_banned_muscles

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class RecommendationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_bmi_calculation(self):
        bmi, category = calculate_bmi(70, 175) # 70kg, 1.75m
        self.assertEqual(bmi, 22.9)
        self.assertEqual(category, "Normal")

        bmi, category = calculate_bmi(95, 175) # Overweight/obese
        self.assertEqual(category, "Obese")

    def test_bmr_and_calorie_target(self):
        # Male BMR: 10 * 80 + 6.25 * 180 - 5 * 30 + 5 = 800 + 1125 - 150 + 5 = 1780
        bmr = calculate_bmr(80, 180, 30, 'Male')
        self.assertEqual(bmr, 1780.0)

        # TDEE (Moderately Active: 1.55): 1780 * 1.55 = 2759
        tdee = calculate_tdee(bmr, 'Moderately Active')
        self.assertEqual(tdee, 2759.0)

        # Calorie Target for Weight Loss: 2759 - 500 = 2259
        target = calculate_calorie_target(tdee, 'Weight Loss')
        self.assertEqual(target, 2259.0)

    def test_banned_muscles_mapping(self):
        banned = get_banned_muscles("Knee pain, Shoulder strain")
        self.assertIn("quads", banned)
        self.assertIn("hamstrings", banned)
        self.assertIn("shoulders", banned)
        self.assertIn("chest", banned)

    def test_recommendation_filtering(self):
        # Seed dummy categories and exercises
        cat = ExerciseCategory(name="Strength", description="Strength exercises")
        db.session.add(cat)
        db.session.flush()

        # Exercise requiring Barbell (Intermediate)
        ex1 = Exercise(
            name="Barbell Bench Press",
            category_id=cat.id,
            target_muscle="Chest",
            difficulty="Intermediate",
            equipment_required="Barbell",
            default_sets=3,
            default_reps=10
        )
        # Exercise requiring Bodyweight (Beginner)
        ex2 = Exercise(
            name="Push-Up",
            category_id=cat.id,
            target_muscle="Chest",
            difficulty="Beginner",
            equipment_required="Bodyweight",
            default_sets=3,
            default_reps=10
        )
        db.session.add_all([ex1, ex2])
        db.session.commit()

        # User profile: Beginner, only has Bodyweight equipment
        user = User(username='fitnessguy', email='fitnessguy@example.com')
        user.set_password('pass')
        db.session.add(user)
        db.session.flush()

        profile = UserProfile(
            user_id=user.id,
            age=25,
            gender='Male',
            height=180,
            weight=75,
            activity_level='Sedentary',
            fitness_goal='General Fitness',
            fitness_level='Beginner',
            available_equipment='Bodyweight',
            training_frequency=1
        )
        db.session.add(profile)
        db.session.commit()

        plan = generate_recommendation(profile)
        
        # Generated plan should only contain Push-Up (bodyweight), not Barbell Bench Press
        plan_exercises = plan.plan_exercises
        exercise_names = [pe.exercise.name for pe in plan_exercises]
        
        self.assertIn("Push-Up", exercise_names)
        self.assertNotIn("Barbell Bench Press", exercise_names)

if __name__ == '__main__':
    unittest.main()
