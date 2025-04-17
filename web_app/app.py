from flask import Flask, redirect, url_for, session
from extensions import db, login_manager
import os

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://FoodLink:Pianoconclusiontown229!@81.109.118.20/FoodLink'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)

# Import and register blueprints
# ----------Could be affected by other app.py files----------
from settings import settings_bp
app.register_blueprint(settings_bp)

# Get or create a test user with a shorter password hash
def get_or_create_test_user():
    from models import User
    
    test_user = User.query.filter_by(email='test@example.com').first()
    if not test_user:
        # Use a simpler hash method or a fixed string for testing
        simple_hash = 'test_password_hash'  # Use a fixed value for testing
        
        test_user = User(
            username='testuser',
            name='Test User',
            email='testuser@example.com',
            password=simple_hash
        )
        db.session.add(test_user)
        db.session.commit()
    
    return test_user

# Create database tables and test user
with app.app_context():
    db.create_all()
    
    # Create test user
    test_user = get_or_create_test_user()
    
    # Create mock notification preferences if needed
    from models import Notification
    notification_prefs = Notification.query.filter_by(user_id=test_user.id).first()
    if not notification_prefs:
        notification_prefs = Notification(user_id=test_user.id)
        db.session.add(notification_prefs)
        db.session.commit()

# Add this to your app.py
@app.route('/dashboard')
def dashboard():
    return "Dashboard will be implemented later"

# Then update the blueprint registration to include this route
app.add_url_rule('/dashboard', 'main.dashboard', dashboard)

# Add a route to automatically log in the test user
@app.route('/')
def auto_login():
    from flask_login import login_user
    user = get_or_create_test_user()
    login_user(user)
    # Store theme in session for template access
    session['theme'] = user.theme
    return redirect(url_for('settings.settings_page'))
    
if __name__ == '__main__':
    app.run(debug=True)