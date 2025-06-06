from alchemy_db import db
from flask_login import UserMixin
from datetime import datetime
import pytz

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
    
    _theme = 'light'

    @property
    def theme(self):
        return self._theme
    
    @theme.setter
    def theme(self, value):
        self._theme = value
    
    @property
    def created_at(self):
        return datetime.now(pytz.utc)  # Just return current time
    
    @property
    def last_login(self):
        return None  # Default to None

class Settings(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    
    # Email notification preference
    email_notifications = db.Column(db.Boolean, default=True)
    
    # Settings types
    fridge_open = db.Column(db.Boolean, default=True)
    expiring_food = db.Column(db.Boolean, default=True)
    recipe_suggestions = db.Column(db.Boolean, default=True)
    temperature_alerts = db.Column(db.Boolean, default=True)
    
    # Temperature range preferences (Celsius)
    min_temperature = db.Column(db.Float, default=1.5)
    max_temperature = db.Column(db.Float, default=4.0)
    
    # Humidity range preferences (in percentage)
    max_humidity = db.Column(db.Float, default=50.0)
    
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
    
