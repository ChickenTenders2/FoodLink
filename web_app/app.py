from flask import Flask, redirect, url_for, session, render_template
from flask_login import login_required, current_user
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
login_manager.login_view = 'login'  # This ensures users are redirected to login when needed

# Import and register the settings blueprint
from settings import settings_bp
app.register_blueprint(settings_bp)

with app.app_context():
    db.create_all()

# Main routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('settings.settings_page'))
    return redirect(url_for('login'))

@app.route('/index')
@login_required
def main_index():
    return render_template('index.html', user=current_user)

@app.route('/utensils')
@login_required
def utensils_page():
    return render_template('utensils.html', user=current_user)

if __name__ == '__main__':
    app.run(debug=True)