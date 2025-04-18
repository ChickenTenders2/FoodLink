from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash

# Import database and user model
from models import db, User

# Import utility functions and forms
from utils import LoginForm, CreateAccountForm, send_verification_code, verification_codes

# Initialize Flask application
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'top secret password dont tell anyone this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://FoodLink:Pianoconclusiontown229!@81.109.118.20/FoodLink'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'foodlink2305@gmail.com'  
app.config['MAIL_PASSWORD'] = 'fmgz nrxz mwul nqju'    
app.config['MAIL_DEFAULT_SENDER'] = 'FoodLink <foodlink2305@gmail.com>'

# Initialize extensions
bootstrap = Bootstrap(app)
db.init_app(app)
mail = Mail(app)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Index route
@app.route('/')
def index():
    return render_template('index.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not check_password_hash(user.password, form.password.data):
            error = "Error: Invalid Credentials"
        else:
            login_user(user, form.remember_me.data)
            session["username"] = form.username.data
            
            # Check if email is verified
            if not user.email_verified:
                flash("Please verify your email address to access all features.", "warning")
                return redirect(url_for('email_verification_page'))
            
            return redirect(url_for('index'))
    
    return render_template('login.html', form=form, error=error)

# Create account route
@app.route('/createAccount', methods=['GET', 'POST'])
def createAccount():
    form = CreateAccountForm()
    msg = ""
        
    if form.validate_on_submit():
        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        
        if existing_user is not None:
            if existing_user.username == form.username.data:
                flash("Username already exists.", "danger")
            if existing_user.email == form.email.data:
                flash("Email already exists.", "danger")
        else:    
            if form.password.data == form.passwordConfirm.data:
                # Create new user
                user = User(
                    username=form.username.data,
                    email=form.email.data,
                    name='null',
                    password=generate_password_hash(form.password.data),
                    email_verified=False
                )
                db.session.add(user)
                db.session.commit()
                
                # Log the user in
                login_user(user)
                
                # Redirect to email verification
                flash("Account created successfully! Please verify your email.", "success")
                return redirect(url_for('email_verification_page'))
            else:
                msg = "Passwords mismatched." 

    return render_template('createAccount.html', form=form, msg=msg)

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('username', None)
    return redirect(url_for('index'))

# Email verification page
@app.route('/email/verification')
@login_required
def email_verification_page():
    return render_template('email_verification.html')

# Route to request verification code
@app.route('/email/send-code', methods=['POST'])
@login_required
def send_verification_code_route():
    # Check if email is already verified
    if current_user.email_verified:
        flash('Your email is already verified.', 'info')
        return redirect(url_for('email_verification_page'))
    
    # Send verification code
    send_verification_code(current_user, mail)
    flash('A verification code has been sent to your email address.', 'success')
    return redirect(url_for('email_verification_page'))

# Route to verify email with code
@app.route('/email/verify-code', methods=['POST'])
@login_required
def verify_code():
    # Get submitted code
    entered_code = request.form.get('verification_code')
    
    if not entered_code:
        flash('Please enter a verification code.', 'danger')
        return redirect(url_for('email_verification_page'))
    
    # Check if code matches
    stored_code = verification_codes.get(current_user.email)
    
    if not stored_code:
        flash('No verification code found. Please request a new code.', 'danger')
        return redirect(url_for('email_verification_page'))
    
    if stored_code == entered_code:
        # Code matches, update verification status
        current_user.email_verified = True
        db.session.commit()
        
        # Clear the code
        verification_codes.pop(current_user.email, None)
        
        flash('Your email has been verified successfully!', 'success')
    else:
        flash('Invalid verification code. Please try again.', 'danger')
    
    return redirect(url_for('email_verification_page'))

if __name__ == '__main__':
    with app.app_context():
        # Test database connection
        try:
            user_count = User.query.count()
            print(f"Connected to database. User count: {user_count}")
        except Exception as e:
            print(f"Database connection error: {e}")
    
    app.run(debug=True)