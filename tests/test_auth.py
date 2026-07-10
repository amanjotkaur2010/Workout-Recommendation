import unittest
from app import create_app
from app.config import Config
from app.models import db
from app.models.user import User

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class AuthTestCase(unittest.TestCase):
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

    def test_registration(self):
        response = self.client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful', response.data)
        
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('password123'))

    def test_login_logout(self):
        # Register user first
        user = User(username='loginuser', email='loginuser@example.com')
        user.set_password('secretword')
        db.session.add(user)
        db.session.commit()

        # Login
        response = self.client.post('/auth/login', data={
            'email_or_username': 'loginuser',
            'password': 'secretword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back', response.data)

        # Logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged out', response.data)

    def test_unauthorized_dashboard_access(self):
        response = self.client.get('/dashboard/', follow_redirects=True)
        # Should redirect to login page
        self.assertIn(b'Log In', response.data)

if __name__ == '__main__':
    unittest.main()
