from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import pytz

# Initialize db, but don't connect it to an app yet
db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'user'  # Explicitly set table name to match MariaDB
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    password = db.Column(db.String(200), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    
    # These properties match what's in your existing code
    @property
    def two_factor_enabled(self):
        return False  # Default to False for simplicity
    
    @property
    def theme(self):
        return 'light'  # Default theme
    
    @property
    def created_at(self):
        return datetime.now(pytz.utc)  # Just return current time
    
    @property
    def last_login(self):
        return None  # Default to None

class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'
    #admin doesnt need email verification
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    #admin does not need the properties an user does

    # allows special privileges for advanced admins to add new admins
    advanced_privileges = db.Column(db.Boolean, default=False)
    