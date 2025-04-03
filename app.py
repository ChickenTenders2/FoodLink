from flask import Flask, redirect, url_for, session, flash
from flask_login import LoginManager, login_required, current_user, login_user
from flask_mail import Mail
import os
from sqlalchemy import inspect, text

# Import db from models
from models import db, User

# Initialize Flask app
app = Flask(__name__)

# Configuration - use the same connection details as in db_setup.py
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://FoodLink:Pianoconclusiontown229!@80.0.43.124/FoodLink'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your_email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your_email_password')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'FoodLink <your_email@gmail.com>')

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import and initialize email verification
from email_verification import email_verification_bp, init_email_verification
init_email_verification(app, db, mail)
app.register_blueprint(email_verification_bp, url_prefix='/email')

# Simple route to test
@app.route('/')
def index():
    return redirect(url_for('email_verification.verification_page'))

# Auto login for testing
@app.route('/auto-login')
def auto_login():
    # Get test user
    test_user = User.query.filter_by(email='test@example.com').first()
    if test_user:
        login_user(test_user)
        session['theme'] = 'light'
        return redirect(url_for('email_verification.verification_page'))
    else:
        flash("Test user not found", "danger")
        return "Test user not found. Make sure you've created the test user in the database."

if __name__ == '__main__':
    with app.app_context():
        # Add email_verified column if it doesn't exist
        try:
            inspector = inspect(db.engine)
            columns = [column['name'] for column in inspector.get_columns('user')]
            
            if 'email_verified' not in columns:
                print("Adding email_verified column to user table...")
                with db.engine.connect() as connection:
                    connection.execute(text("ALTER TABLE user ADD COLUMN email_verified BOOLEAN DEFAULT FALSE"))
                    connection.commit()
                print("Column added successfully")
        except Exception as e:
            print(f"Error checking or adding email_verified column: {e}")
    
    # Create a test user if it doesn't exist
    with app.app_context():
        try:
            test_user = User.query.filter_by(email='test@example.com').first()
            if not test_user:
                print("Creating test user...")
                # Creating a user that matches the structure of your User model
                test_user = User(
                    username='testuser',
                    email='test@example.com',
                    name='Test User',
                    password='test_password_hash',  # In a real app, this would be hashed
                    email_verified=False
                )
                db.session.add(test_user)
            else:
                # Reset the email verification status on server restart
                print("Resetting test user email verification status...")
                test_user.email_verified = False
                
            db.session.commit()
            print("Test user setup complete")
        except Exception as e:
            print(f"Error setting up test user: {e}")
    
    app.run(debug=True)