from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import session
from models import User, Admin

# SQLAlchemy for database management
db = SQLAlchemy()
# Flask-Login for managing user sessions
login_manager = LoginManager()

# Load user to database based on user ID (or admin ID if admin login)
@login_manager.user_loader
def load_user(user_id):
    user_type = session.get("user_type")

    if user_type == "admin":
        return Admin.query.get(int(user_id))
    elif user_type == "user":
        return User.query.get(int(user_id))