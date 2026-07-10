from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db
from app.models.user import User, UserProfile
from app.models.progress import UserPreference

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')
            
        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'danger')
            return render_template('auth/register.html')
            
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/register.html')
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
            
        # Check existing user
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('Username already exists.', 'danger')
            return render_template('auth/register.html')
            
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')
            
        # Create user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        # Check if first user in db, make admin
        if User.query.count() == 0:
            new_user.is_admin = True
            
        db.session.add(new_user)
        db.session.flush() # Populate new_user.id
        
        # Create standard profile and preference defaults
        new_profile = UserProfile(user_id=new_user.id, water_target=2500.0)
        new_preference = UserPreference(user_id=new_user.id, dark_mode=True)
        
        db.session.add(new_profile)
        db.session.add(new_preference)
        db.session.commit()
        
        # Log the user in and redirect to complete profile
        login_user(new_user)
        flash('Registration successful! Please complete your fitness profile.', 'success')
        return redirect(url_for('dashboard.profile'))
        
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        email_or_username = request.form.get('email_or_username', '').strip()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False
        
        if not email_or_username or not password:
            flash('Please fill in all fields.', 'danger')
            return render_template('auth/login.html')
            
        # Find user by email or username
        user = User.query.filter((User.email == email_or_username) | (User.username == email_or_username)).first()
        
        if not user or not user.check_password(password):
            flash('Invalid username/email or password.', 'danger')
            return render_template('auth/login.html')
            
        login_user(user, remember=remember)
        flash(f'Welcome back, {user.username}!', 'success')
        
        # Check if profile is complete, if not prompt them
        if not user.profile or not user.profile.age:
            return redirect(url_for('dashboard.profile'))
            
        return redirect(url_for('dashboard.index'))
        
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
