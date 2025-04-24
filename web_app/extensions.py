from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import session

# SQLAlchemy for database management
db = SQLAlchemy()
# Flask-Login for managing user sessions
login_manager = LoginManager()
