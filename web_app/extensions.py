from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# SQLAlchemy for database management
db = SQLAlchemy()
# Flask-Login for managing user sessions
login_manager = LoginManager()

# Load user to database based on user ID
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))