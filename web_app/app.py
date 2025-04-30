### general imports for flask setup
from flask import Flask, jsonify, render_template, request, url_for, Response, redirect, session, flash
from flask_bootstrap import Bootstrap
import os

### shared operations for user and admin:
# for scanning items (barcode or ai object recogniser)
import scanner
# for checking item image exists
from os.path import isfile as file_exists
import item

### user operations
import tool
import inventory
import notification
import shopping
# for getting temperature and humidity of fridge
import thingsboard
# for alerting when item is added on raspberry pi screen
import success
# for recipe handling
import recipe as recipe_sql
import recipe_processing
# for parsing ingredients and tools list of lists as string
import json

### admin operations
# for admin, item and recipe view
import admin_recipe
import input_handling
# for report handling
import report

### for login systems
# general flask login functions
from flask_login import login_required, current_user, login_user, logout_user, LoginManager
# for email verification
from flask_mail import Mail
from email_verification import send_verification_code
# for user lockout after too many attempts
from time import time as current_time
# for validating password complexity (regular expression checker)
from re import search as re_search
# for encrypting password
from werkzeug.security import generate_password_hash, check_password_hash
# for storing user variables in server side session
from flask_session import Session
# for accessing database (via alchemy)
from alchemy_db import db, safe_execute
from models import User, Admin
# login forms
from flask_forms import LoginForm, CreateAccountForm, CombinedResetForm, ResetPasswordForm, AdminCreateForm, AdminPasswordForm

# for closing db connection on exit
from database import close_connection
import atexit
atexit.register(close_connection)

# Import database and user model
app = Flask(__name__, template_folder = "templates")

# Initialize Flask-Session
app.config["SESSION_PERMANENT"] = False     
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://FoodLink:Pianoconclusiontown229!@80.0.43.124/FoodLink'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'foodlink2305@gmail.com'  
app.config['MAIL_PASSWORD'] = 'ngjw ejzx cfwn wnew'    
app.config['MAIL_DEFAULT_SENDER'] = 'FoodLink <foodlink2305@gmail.com>'
mail = Mail(app)

# Import and register the settings blueprint (i'm sorry it wasnt me :( )
from settings import settings_bp
app.register_blueprint(settings_bp)

# Initialize extensions
bootstrap = Bootstrap(app)

# Flask-Login for managing user sessions
login_manager = LoginManager()
login_manager.init_app(app)
# This ensures users are redirected to login when needed (used by @login_required decorator)
login_manager.login_view = 'login' 
db.init_app(app)

# clears alchemy db session after every request so errors dont occur
# helps stop crashing when clicking between pages fast
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

# Load user to database based on user ID (or admin ID if admin login)
@login_manager.user_loader
def load_user(user_id):
    user_type = session.get("user_type")

    if user_type == "admin":
        return safe_execute(db.session.get, Admin, int(user_id))
    elif user_type == "user":
        return safe_execute(db.session.get, User, int(user_id))


###     DECORATOR FUNCTIONS TO STOP UNAUTHORISED ACCESS TO PAGES

## for admin only pages
def admin_only(f):
    def decorated_function(*args, **kwargs):
        ## if the admin isnt signed in
        if not current_user.is_authenticated:
            flash("You must be logged in to access that page.", "warning")
            ## redirect to admin login
            return redirect(url_for("admin_login"))
        ## if the user tries to access the page
        elif not isinstance(current_user._get_current_object(), Admin):
            flash("You do not have permission to access that page.", "danger")
            ## send them back to dashboard
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    ## makes sure route function is unique
    decorated_function.__name__ = f.__name__
    return decorated_function

## for user only pages
def user_only(f):
    def decorated_function(*args, **kwargs):
        ## if the user isnt logged in
        if not current_user.is_authenticated:
            flash("You must be logged in to access that page.", "warning")
            ## redirect to login page
            return redirect(url_for("login"))
        ## if an admin tries to access a normal account page
        if isinstance(current_user._get_current_object(), Admin):
            flash("Admins cannot access that page.", "danger")
            ## redirect to dashboard
            return redirect(url_for("AdminDashboard"))
        # stops unverified users from accessing features
        if not current_user.email_verified:
            flash("Please verify your email before accessing other features.", "warning")
            return redirect(url_for("email_verification_page"))
        return f(*args, **kwargs)
    ## makes sure route function is unique
    decorated_function.__name__ = f.__name__
    return decorated_function

# for shared routes (user and admin) make user user email is verified
# and account also logged in
def verified_only(f):
    def decorated_function(*args, **kwargs):
        # makes sure admin or user is logged in
        if not current_user.is_authenticated:
            flash("You must be logged in to access this page.", "warning")
            return redirect(url_for("login"))
        # makes sure email is verified for user accounts
        user_obj = current_user._get_current_object()
        if isinstance(user_obj, User) and not user_obj.email_verified:
            flash("Please verify your email before accessing this page.", "warning")
            return redirect(url_for("email_verification_page"))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# for email verification pages
def unverified_only(f):
    def decorated_function(*args, **kwargs):
        # makes sure user is logged in
        if not current_user.is_authenticated:
            flash("You must be logged in to access this page.", "warning")
            return redirect(url_for("login"))
        # makes sure account is not already verified (admin emails are always verified)
        user_obj = current_user._get_current_object()
        if isinstance(user_obj, Admin):
            flash("Your email is already verified!", "warning")
            return redirect(url_for("AdminDashboard"))
        if user_obj.email_verified:
            flash("Your email is already verified!", "warning")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Index route
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    else:
        # user is not logged in
        return redirect(url_for('login'))


### ADMIN ACCOUNT SYSTEM ROUTES

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    error = None
    
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and check_password_hash(admin.password, form.password.data):
            login_user(admin, remember=False)
            session["user_type"] = "admin"
            flash("Logged in successfully as admin.", "success")
            return redirect(url_for("AdminDashboard"))
        else:
            error = "Invalid admin credentials."

    return render_template('admin_login.html', form=form, error=error)

@app.route("/admin/add", methods=["GET", "POST"])
@admin_only
def AddAdmin():
    # Must be advanced admin to add new admins
    if not current_user.advanced_privileges:
        flash("You are not authorized to add new admins.", "danger")
        return redirect(url_for("AdminDashboard"))

    form = AdminCreateForm()
    message = None

    if form.validate_on_submit():
        # Check password complexity
        password = form.password.data
        if len(password) >= 6 and sum(c.isdigit() for c in password) >= 2 and re_search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            # Check if username or email already exist
            existing_admin = Admin.query.filter(
                (Admin.username == form.username.data) | 
                (Admin.email == form.email.data)
            ).first()

            if existing_admin:
                message = "Admin already exists."
            else:
                new_admin = Admin(
                    name=form.name.data,
                    username=form.username.data,
                    email=form.email.data,
                    password=generate_password_hash(form.password.data),
                    advanced_privileges=form.advanced_privileges.data,
                )
                safe_execute(db.session.add, new_admin)
                safe_execute(db.session.commit)
                flash("New admin added successfully!", "success")
                return redirect(url_for('AdminDashboard'))
        else:
            message = "Password format error: Password must be at least 6 characters, include at least 2 numbers, and 1 special character."

    return render_template("admin_add.html", form=form, message=message)

@app.route("/admin/update-password", methods=["GET", "POST"])
@admin_only
def AdminUpdatePassword():
    form = AdminPasswordForm()
    message = None

    if form.validate_on_submit():
        new_password = form.new_password.data
        if not check_password_hash(current_user.password, form.current_password.data):
            message = "Current password is incorrect."
        elif form.new_password.data != form.confirm_password.data:
            message = "New passwords do not match."
        elif not (len(new_password) >= 6 and sum(c.isdigit() for c in new_password) >= 2 and re_search(r"[!@#$%^&*(),.?\":{}|<>]", new_password)):
            message = "Password must be at least 6 characters, include at least 2 numbers, and 1 special character."
        else:
            current_user.password = generate_password_hash(form.new_password.data)
            safe_execute(db.session.commit)
            flash("Password updated successfully!", "success")
            return redirect(url_for("AdminDashboard"))

    return render_template("admin_update_password.html", form=form, message=message)

@app.route("/admin/dashboard")
@admin_only
def AdminDashboard():
    return render_template("admin_dashboard.html")

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    if session["user_type"] == "admin":
        url = url_for('admin_login')
    elif session["user_type"] == "user":
        url = url_for("login")
    session.pop("user_type")
    return redirect(url)


###  USER ACCOUNT SYSTEM ROUTES ###
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    
    if "userFailedAttempts" not in session:
        session["userFailedAttempts"] = 0
    if "userLockoutTime" not in session:
        session["userLockoutTime"] = None


    lockoutThrehold = 5  # Number of allowed failed attempts
    lockoutDuration = 60  # Lockout time in seconds (1 minute)
    
    if session["userLockoutTime"] and current_time() >= session["userLockoutTime"]:
        session["userLockoutTime"] = None
        session["userFailedAttempts"] = 0


    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()

        if user is None:
            error = "Error: Invalid Credentials User"
        else:
            if session["userLockoutTime"] and current_time() < session["userLockoutTime"]:
                error = "Account tempororily locked. Please try again later."
            else:
                if not check_password_hash(user.password, form.password.data):
                    session["userFailedAttempts"] += 1
                    attempt = session["userFailedAttempts"]
                    if session["userFailedAttempts"] >= lockoutThrehold:
                        session["userLockoutTime"] = current_time() + lockoutDuration
                        error = f"Account locked for {lockoutDuration} seconds due to multiple failed attempts."
                    else:
                        error = f"Error: Invalid Credentials PWD {attempt}"
                else:
                    login_user(user, form.remember_me.data)
                    # sets user_type for load user function
                    session["user_type"] = "user"
                    
                    session["userFailedAttempts"] = 0
                    session["userLockoutTime"] = None
                  # Check if email is verified
                    if not user.email_verified:
                        flash("Please verify your email address to access all features.")
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
                msg = "Username already exists."
            if existing_user.email == form.email.data:
                msg = "Email already exists."
        else:    
            if len(form.password.data) >= 6 and sum(c.isdigit() for c in form.password.data) >= 2 and re_search(r"[!@#$%^&*(),.?\":{}|<>]", form.password.data):
                if form.password.data == form.passwordConfirm.data:
                    # Create new user
                    user = User(
                        username=form.username.data,
                        email=form.email.data,
                        name='null',
                        password=generate_password_hash(form.password.data),
                        email_verified=False
                    )
                    safe_execute(db.session.add, user)
                    safe_execute(db.session.commit)
                    
                    # Log the user in
                    login_user(user)
                    session["user_type"] = "user"
                    
                    # Redirect to email verification
                    flash("Account created successfully! Please verify your email.")
                    return redirect(url_for('email_verification_page'))
                else:
                    msg = "Passwords mismatched." 
            else:
                msg = "Password format error: Password must be at least 6 characters long, include 2 numbers, and 1 special character required"    

    return render_template('createAccount.html', form=form, msg=msg)


@app.route('/resetByEmail', methods=['GET', 'POST'])
def resetByEmail():
     
    form = CombinedResetForm()
    error = None

    if form.submit_email.data and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_verification_code(user, mail, "reset")
            flash("Verification code sent to your email.")
            error = "Verification code sent to your email."
        else:
            error = "Invalid email address."

    elif form.submit_otp.data and form.validate():
        user = User.query.filter_by(email=form.email.data).first()

        if user and session.get("verification_codes", {}).get(user.email) == form.otp.data:
            # removes code if correct
            session["verification_codes"].pop(user.email, None)
            session.modified = True
            session['reset_email'] = user.email
            return redirect(url_for('resetPassword'))
        else:
            error = "Invalid verification code."

    return render_template('resetByEmail.html', form=form, error=error)

            

@app.route('/resetPassword', methods=['GET', 'POST'])
def resetPassword():
   
    form = ResetPasswordForm()
    email = session.get('reset_email')
    error = None
    if not email:
        flash("Session expired or invalid.")
        return redirect(url_for('resetByEmail'))
        
   
    user = User.query.filter_by(email=email).first()

     
    if user is None:
        flash("Invalid session or email. Please try again.")
        return redirect(url_for('resetByEmail'))

  

    if form.validate_on_submit():
        if len(form.password.data) >= 6 and sum(c.isdigit() for c in form.password.data) >= 2 and re_search(r"[!@#$%^&*(),.?\":{}|<>]", form.password.data):
            if form.password.data == form.passwordConfirm.data:
                print("Setting new password")
                user.password = generate_password_hash(form.password.data)
                safe_execute(db.session.commit)

                session.pop('reset_email', None)

                error = "Your password has been successfully reset."
                return redirect(url_for('login'))  
            else:
                print("Form errors:", form.errors)
                error = "Passwords do not match. Please try again."
        else:     
            error = "Password format error: Password must be at least 6 characters long, include 2 numbers, and 1 special character required"    
   

    return render_template('resetPassword.html', form=form, error=error)

# Email verification page
@app.route('/email/verification')
@unverified_only
def email_verification_page():
    return render_template('email_verification.html')

# Route to request verification code
@app.route('/email/send-code', methods=['POST'])
@unverified_only
def send_verification_code_route():
    # Send verification code
    send_verification_code(current_user, mail, 'verify')
    flash('A verification code has been sent to your email address.', 'success')
    return redirect(url_for('email_verification_page'))

# Route to verify email with code
@app.route('/email/verify-code', methods=['POST'])
@unverified_only
def verify_code():
    # Get submitted code
    entered_code = request.form.get('verification_code')
    
    if not entered_code:
        flash('Please enter a verification code.', 'danger')
        return redirect(url_for('email_verification_page'))
    
    # Check if code matches
    stored_code = session.get("verification_codes", {}).get(current_user.email)
    
    if not stored_code:
        flash('No verification code found. Please request a new code.', 'danger')
    
    if stored_code == entered_code:
        # Code matches, update verification status
        current_user.email_verified = True
        safe_execute(db.session.commit)
        
        # Clear the code
        session["verification_codes"].pop(current_user.email, None)
        session.modified = True
        
        flash('Your email has been verified successfully!', 'success')
        return redirect(url_for("select_tools"))
    else:
        flash('Invalid verification code. Please try again.', 'danger')
    
    return redirect(url_for('email_verification_page'))
    


### SETTINGS PAGE ROUTE

@app.route('/settings')
@user_only
def settings_page():
    return redirect(url_for('settings.settings_page'))


#### USER DASHBOARD ROUTES

@app.route('/dashboard', methods=['GET', 'POST'])
@user_only
def dashboard():
    # display realtime temperature and humidity sensor data
    temp_url = "https://thingsboard.cs.cf.ac.uk/dashboard/9c597b10-0b04-11f0-8ef6-c9c91908b9e2?publicId=0d105160-0daa-11f0-8ef6-c9c91908b9e2" 
    humid_url = "https://thingsboard.cs.cf.ac.uk/dashboard/74d87180-0dbc-11f0-8ef6-c9c91908b9e2?publicId=0d105160-0daa-11f0-8ef6-c9c91908b9e2"

    return render_template('index.html', temp_url=temp_url, humid_url = humid_url)

# marks the notifaction as read upon user click
@app.route('/notification/mark_read', methods=['POST'])
@user_only
def mark_read_notification():
    notif_id = request.json.get('notif_id')
    if not notif_id:
        return jsonify({'success': False, 'error': 'Notification ID missing'}), 400
    result = notification.mark_read(notif_id)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)

@app.context_processor
def inject_notifications(): 
    # ensure the user is logged in
    if current_user.is_authenticated and isinstance(current_user._get_current_object(), User): 
        user_id = current_user.id
        #trgigger temperature/humidity notifications
        notification.temperature_humidity_notification(user_id, None, None) 
        # trigger expiry notifications
        notification.expiry_notification(user_id) 
        result = notification.get_notifications(user_id) 
        if not result.get("success"):
            return dict(notifications=[], unread_count=0)
        notifications = result.get("notifications")
        unread_count = sum(1 for n in notifications if n[4] == 0) 
        # inject into all templates as global context variable
        return dict(notifications=notifications, unread_count=unread_count)  
    else:
        # return empty values is user is unauthticated
        return dict(notifications=[], unread_count=0)

# Dynamtically update notification bar
@app.route('/get_notifications', methods=['GET', 'POST']) 
@user_only
def get_notifications():
    # retrieving sensor data from telemetry by connecting to thingsboard using JWT token
    device_id = "15b7a650-0b03-11f0-8ef6-c9c91908b9e2"
    user_id = current_user.id
    token = thingsboard.get_jwt_token()
    if token:
        data = thingsboard.get_telemetry(token, device_id)
        if data:
            temperature = float(data['temperature'][0]['value'])
            humidity = float(data['humidity'][0]['value'])
            notification.temperature_humidity_notification(user_id, temperature, humidity)
    
    # check for any new expiry alerts
    notification.expiry_notification(user_id)

    # fetch notifications
    result = notification.get_notifications(user_id) 
    if not result.get("success"):
        return jsonify(result), 500
    
    notifications = result.get("notifications", [])

    # get number of unread notification
    unread_count = sum(1 for n in notifications if n[4] == 0)

    # return data in json format for dynamic updating
    return jsonify({
        'notifications': [
            {
                'id': n[0],
                'message': n[2],
                'timestamp': n[3].strftime('%Y-%m-%d %H:%M'),
                'severity': n[5],
                'read': n[4] == 1
            }
            for n in notifications
        ],
        'unread_count': unread_count
    })
  
### INVENTORY ROUTES ###

# Inventory interface
@app.route('/inventory/')
@user_only
def get_inventory():
    return render_template("inventory.html")

# allows for no search query to be entered
@app.route('/inventory/get/', defaults={'search_query': None})
@app.route('/inventory/get/<search_query>')
# used to dynamically get inventory
@user_only
def api_inventory(search_query = None):
    user_id = current_user.id
    if search_query:
        # searches for an item if query is provided otherwise gets all items
        result = inventory.search_items(user_id, search_query)
    else:
        result = inventory.get_items(user_id)

    if not result.get("success"):
        return jsonify(result), 500

    return jsonify(result)

# Add item to inventory interface
@app.route("/inventory/add_item/")
@user_only
def add_to_inventory():
    return render_template("inventory_add.html")

# Add item to inventory
@app.route("/inventory/add_item/add", methods=["POST"])
@user_only
def append_inventory():
    user_id = current_user.id
    item_id = request.form.get("item_id")
    if not item_id:
        return jsonify({"success": False, "error": "Item ID is required."}), 400
    
    result = inventory.process_add_form(user_id, item_id, request.form)
    if not result.get("success"):
        if result.get("error") == "An internal error occurred.":
            return jsonify(result), 500
        else:
            return jsonify(result), 400
    # displays success alert on raspberry pi display
    success.send_success_alert()
    return jsonify(result)

# Update quantity and expiry of item in inventory
@app.route('/inventory/update_item', methods = ['POST'])
@user_only
def update_item(): 
    # gets variables needed to update item
    inventory_id = request.form.get('inventory_id')
    quantity = request.form.get('quantity')
    expiry_date = request.form.get('expiry_date')

    if not inventory_id or not quantity or not expiry_date:
        return jsonify({"success": False, "error": "Form was missing a value"}), 400
    
    # Update the database with new quantity and expiry date
    result = inventory.update_item(inventory_id, quantity, expiry_date)
    # returns response to js code
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)

@app.route('/inventory/remove_item', methods=['POST'])
@user_only
def remove_item():
    inventory_id = request.form.get('inventory_id')
    if not inventory_id:
        return jsonify({"success": False, "error": "Form was missing inventory ID."}), 400
    
    result = inventory.remove_item(inventory_id)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)

@app.route("/inventory/add_item/new", methods = ["POST"])
@user_only
def new_item():
    user_id = current_user.id
    result = item.process_add_form(request.form, user_id)
    item_id = result.get("item_id")

    # if the item was not succesffuly added to the item table
    if not result.get("success"):
        if result.get("error") == "An internal error occurred.":
            return jsonify(result), 500
        else:
            return jsonify(result), 400
    else:
        # gets image if uploaded otherwise equals none
        image = request.files.get("item_image")
        original_item_id = request.form.get("item_id") or None
        # adds image if uploaded or uses cloned image if possible
        item.add_item_image(image, item_id, original_item_id)
    
    if not request.form.get("add_to_inventory"):
        return jsonify({"success": True, "item_id": item_id, "message": "Item added to personal items."})
    
    result = inventory.process_add_form(user_id, item_id, request.form)
    if result.get("success"):
        return jsonify({"success": True, "item_id": item_id, "message": "Item added to inventory and personal items."})
    else:
        return jsonify(result)

@app.route("/inventory/add_item/update", methods = ["POST"])
@user_only
def update_item_information():
    user_id = current_user.id
    item_id = request.form.get("item_id")
    result = item.process_update_form(item_id, request.form, user_id)

    # if the item was not succesffuly added to the item table
    if not result.get("success"):
        if result.get("error") == "An internal error occurred.":
            return jsonify(result), 500
        else:
            return jsonify(result), 400
    else:
        # gets image if uploaded otherwise equals none
        image = request.files.get("item_image")
        # adds image if uploaded
        item.add_item_image(image, item_id)
    
    if not request.form.get("add_to_inventory"):
        return jsonify({"success": True, "message": "Personal item updated."})
    
    result = inventory.process_add_form(user_id, item_id, request.form)
    if result.get("success"):
        return jsonify({"success": True, "message": "Personal item updated and added to inventory."})
    else:
        return jsonify(result)
    
@app.route("/inventory/update_items_quantity", methods=["POST"])
@user_only
def update_quantities():
    items_used_string = request.form.get("items_used")

    # list variables must be stringified client side so lists transfer correctly
    # they are so decoded to get original data type back
    items_used = json.loads(items_used_string)

    if not (items_used):
        return jsonify({"success": False, "error": "No items added."})

    # performs updates function (set to amount or removes if quantity <= 0)
    result = inventory.update_quantities(items_used)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)

@app.route("/inventory/delete_item/<item_id>")
@user_only
def user_delete_item(item_id):
    user_id = current_user.id
    result = item.remove_item(item_id, user_id)
    if not result.get("success"):
        if result.get("error") == "Permission denied.":
            return jsonify(result), 403 # forbidden
        return jsonify(result), 500
    return jsonify({"success": True, "message": "Item deleted and removed from inventory."})


# ### BARCODE SCANNING ROUTES ###

# Opens camera module and returns feed
@app.route('/scanner/get')
@verified_only
def get_scanner():
    return Response(scanner.scan(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Closes camera module
@app.route('/scanner/close')
@verified_only
def close_scanner():
    scanner.release_capture()
    return jsonify({"success":True})

# Returns the barcode number if one is found or item name if object recognised
@app.route('/scanner/get_object')
@verified_only
def get_object():
    object = scanner.get_scanned()
    if (object):
        scanner.clear_scanned()
        return jsonify({"success": True, "object": object})
    else:
        return jsonify({"success": False})

@app.route("/unpause_scanner")
@verified_only
def unpause_scanner():
    scanner.unpause_scanner()
    return jsonify({"success":True})

@app.route("/scanner/toggle_mode/<value>")
@verified_only
def toggle_scan_mode(value):
    if value == "true":
        scanner.toggle_mode(True)
        return jsonify({"success": True})
    elif value == "false":
        scanner.toggle_mode(False)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})


### ITEM ROUTES ###
    
@app.route("/items/get_personal")
@user_only
def get_personal():
    user_id = current_user.id
    result = item.get_personal(user_id)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)

@app.route("/items/single_text_search/<item_name>")
@user_only
def single_item_search(item_name):
    user_id = current_user.id
    result = item.text_single_search(user_id, item_name)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)


# Get items by text search
@app.route("/items/text_search/<search_term>")
@user_only
def text_search(search_term):
    user_id = current_user.id
    if not search_term:
        return jsonify({"success": False, "error": "No search term provided."}), 400
    
    result = item.text_search(user_id, search_term)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)

# Get item by barcode search
@app.route("/items/barcode_search/<barcode>")
@user_only
def get_item_by_barcode(barcode):
    user_id = current_user.id

    # Ensure barcode is digits only
    if not barcode.isdigit():
        return jsonify({"success": False, "error": "Invalid barcode format."}), 400
    
    result = item.barcode_search(user_id, barcode)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)

# Get item by id
@app.route("/items/get_item/<item_id>")
@admin_only
def get_item(item_id):
    result = item.get_item(item_id)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)

# Add item interface
@app.route('/items/add_item')
@admin_only
def add_item():
    return render_template("add_item.html")

# Add item to item table
@app.route('/items/add_item/add', methods=["POST"])
@admin_only
def append_item_db():
    result = item.process_add_form(request.form)
    if not result.get("success"):
        if result.get("error") == "An internal error occurred.":
            return jsonify(result), 500
        else:
            return jsonify(result), 400
    
    item_id = result.get("item_id")
    # gets image if uploaded otherwise equals none
    image = request.files.get("item_image")
    # adds image if uploaded
    item.add_item_image(image, item_id)
    # item id does not need to be returned
    return jsonify({"success": True})

# Check if item has an image
@app.route("/items/find_image/<item_id>")
@verified_only
def find_image(item_id):
    path = f"static/images/{item_id}.jpg"
    exists = file_exists(path)
    return jsonify({"success": exists})


### ITEM REPORT ROUTES

@app.route("/items/reports/new", methods=["POST"])
@user_only
def report_item():
    user_id = current_user.id
    new_item_id = request.form.get("new_item_id")
    item_id = request.form.get("item_id") or None

    if not new_item_id:
        return jsonify({"success": False, "error": "No item ID provided."}), 400
    
    result = report.add_report(new_item_id, item_id, user_id)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)

@app.route("/items/reports")
@admin_only
def display_reports():
    return render_template("reports.html")

@app.route("/items/reports/get")
@admin_only
def get_reports():
    result = report.get_reports()
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)

@app.route("/items/reports/check_assigned/<new_item_id>")
@admin_only
def check_assigned(new_item_id):
    result = report.check_assigned(new_item_id)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)

@app.route("/items/reports/assign/<new_item_id>")
@admin_only
def report_assign(new_item_id):
    admin_id = current_user.id
    result = report.assign(new_item_id, admin_id)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)

@app.route("/items/reports/<new_item_id>/<item_id>")
@admin_only
def display_report(new_item_id, item_id):
    return render_template("report.html", new_item_id = new_item_id, item_id = item_id)

@app.route("/items/reports/resolve", methods=["POST"])
@admin_only
def resolve_report():
    action = request.form.get("action")
    barcode = request.form.get("barcode") or None
    new_item_id = request.form.get("new_item_id")
    original_item_id = request.form.get("item_id") or None
    # gets image if uploaded otherwise equals none
    image = request.files.get("item_image")
    # if the missing item reported isnt elligible for being added 
    if action == "deny" and original_item_id is None:
        # gets the reports
        result = report.get_reports_by(new_item_id)
        if not result.get("success"):
            return jsonify(result), 500
        reports = result.get("reports")
        # report will be singular
        _, personal_item_name, user_id = reports[0]
        # removes the report
        result = report.remove_report(new_item_id)
        if not result.get("success"):
            return jsonify(result), 500
        # notification message
        message = lambda item_name : f"""Thank you for reporting the missing item, {item_name}. 
                    Unfortunately, your item is not currently elligible to be added at this time.
                    However, you can still continue to use your personal item. 
                    """

        # notify user of the change
        result = notification.support_notification(user_id, message(personal_item_name))
        if not result.get("success"):
            return jsonify(result), 500
        return jsonify(result)
        
    # if the proposed error was with an item having incorrect information (misinformation)
    if original_item_id:
        # if the original item had an error
        if action == "approve":
            # updates original item with correct information if approved
            # sets the user_id = null for the item so it appears for all users
            result = item.process_update_form(original_item_id, request.form)
            if not result.get("success"):
                return jsonify({"success": False, "error": "Error updating item information."}), 500
            # updates image if uploaded
            item.add_item_image(image, original_item_id)
            # notification message
            message = lambda item_name : f"""Thank you for reporting an error with item, {item_name}. 
                        Your personal item has been successfully replaced."""
        # if original item was already correct
        else:
            # notification message
            message = lambda item_name : f"""Thank you for reporting an error with item, {item_name}. 
                    However the original item was already correct! 
                    Please be careful to double check before reporting an item.
                    Your personal item has been successfully replaced."""

        # id of item to replace personal items with
        replace_id = original_item_id

        # finds reports that report the original item
        result = report.get_reports_by(new_item_id, original_item_id, "id")
        if not result.get("success"):
            return jsonify(result), 500
        duplicate_reports = result.get("reports")

    # if the error was a missing item and it got approved
    else:
        # adds the missing item to the table
        # sets the user_id = null for the item so it appears for all users
        result = item.process_add_form(request.form)
        if not result.get("success"):
                return jsonify({"success": False, "error": "Error adding new item."}), 500
        # gets the id to replace the personal items with
        replace_id = result.get("item_id")

        # adds image if uploaded or uses users personal item image if possible
        item.add_item_image(image, replace_id, new_item_id)

        # notification message
        message = lambda item_name : f"""Thank you for reporting the missing item, {item_name}.
                    Your request has been approved!
                    Your personal item has been successfully replaced."""

        # find other reports that reported the missing item
        # finds by same barcode as their is no original item for missing items
        # also searches using the new_item_id incase the item has no barcode
        result = report.get_reports_by(new_item_id, barcode, "barcode")
        if not result.get("success"):
            return jsonify(result), 500
        duplicate_reports = result.get("reports")

    # gets the limit that a users item can have for quantity
    result = item.get_default_quantity(replace_id)
    if not result.get("success"):
            return jsonify(result), 500
    default_quantity = result.get("quantity")

    # for each report of an item
    for personal_item_id, personal_item_name, user_id in duplicate_reports:
        # replace the personal item the user made with the now corrected / new item
        result = inventory.correct_personal_item(personal_item_id, replace_id, default_quantity)
        if not result.get("success"):
            return jsonify(result), 500
        # removes the users personal item as it is no longer needed
        result = item.remove_item(personal_item_id)
        if not result.get("success"):
            # detailed report of error for admins
            return jsonify({"success": False, 
                            "error": f"""[remove_item_sql error]:
                            Occured for user id: {user_id}.
                            Inputs: personal_item_id: {personal_item_id}."""
                            }), 500
        # removes the report
        result = report.remove_report(personal_item_id)
        if not result.get("success"):
            return jsonify(result), 500
        # notify user of the change
        result = notification.support_notification(user_id, message(personal_item_name))
        if not result.get("success"):
            return jsonify(result), 500

    return jsonify({"success": True})
    

#### ADMIN VIEW ITEMS AND RECIPES ROUTES

# Item table interface
@app.route('/admin/item_view')
@admin_only
def get_items():
    result = item.get_page(0)
    if not result.get("success"):
        return result, 500
    items = result.get("items")
    result = item.get_max_page()
    if not result.get("success"):
        return result, 500
    max_pages = result.get("max")
    return render_template("item_view.html", items = items, max = max_pages)

# allows for no search query to be entered
@app.route('/admin/item_view/get', defaults={'search_query': None})
@app.route('/admin/item_view/get/<search_query>')
@admin_only
def search_items(search_query = None):
        # Checks if the search is for a specifc page.
        if search_query.isnumeric():
            result = item.get_max_page()
            if not result.get("success"):
                return result, 500
            max_pages = result.get("max")
            page = int(search_query)
            # error checking: makes sure page is in bounds
            if page < 0:
                page = 0
            elif page > max_pages:
                page = max_pages
            result = item.get_page(page)
            if not result.get("success"):
                return result, 500
            items = result.get("items")
            # Renders the page with the given index query.
            return render_template("item_view.html", items = items, max = max_pages)
        else:
            # Searches for an item if query is provided otherwise gets all items.
            result = item.get_item_from_name(search_query)
            if not result.get("success"):
                return jsonify(result), 500
            items = result.get("items")
            if items != [None]:
                return render_template("item_view_search.html", items = items)
            else:
                return render_template("item_view_search.html", items = [])
        
# Recipe table interface
@app.route('/admin/recipe_view')
@admin_only
def admin_get_recipes():
    result = admin_recipe.get_all()
    if not result.get("success"):
        return jsonify(result), 500
    recipes = result.get("recipes")
    return render_template("recipe_view.html", recipes = recipes)

@app.route('/admin/recipe_view/gets_items/<int:recipe_id>', methods=['GET'])
@admin_only
def get_ingredients(recipe_id):
    result = recipe_sql.get_recipe_items(recipe_id)
    if not result.get("success"):
        return jsonify(result), 500
    ingredients = result.get("items")
    return jsonify(ingredients)

@app.route('/admin/recipe_view/get_tools_ids/<int:recipe_id>', methods=['GET'])
@admin_only
def get_tools_ids(recipe_id):
    result = recipe_sql.get_recipe_tools(recipe_id)
    if not result.get("success"):
        return jsonify(result), 500
    tools = result.get("tool_ids")
    return jsonify(tools)

# Returns the tools as a dictionary so that names can be mapped to ids in the js code. 
@app.route('/admin/recipe_view/get_tools/', methods=['GET'])
@admin_only
def admin_get_tools():
    result = tool.get_tools()
    if not result.get("success"):
        return jsonify(result), 500
    tools = result.get("tools")
    tools = dict(tools)
    return jsonify(tools)

# Removes an item from the item table.
@app.route('/admin/item_view/delete', methods = ['POST'])
@admin_only
def delete_item():
    # Form data is formatted in utf-8 so it needs to be decoded.
    id = request.data.decode('utf-8')
    result = item.remove_item(id)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)
    
# Removes an item from the item table.
@app.route('/admin/recipe_view/delete', methods = ['POST'])
def delete_recipe():
    # Form data is formatted in utf-8 so it needs to be decoded since id was not submitted in a form.
    id = request.data.decode('utf-8')
    result = admin_recipe.remove_recipe(id)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)
        

# Updates the details of a selected item in the item table.
@app.route('/admin/item_view/update_item', methods = ['POST'])
@admin_only
def update_item_admin(): 
    # Sanitise the input to prevent sql injection.
    sanitised_fields = input_handling.sanitise_all(['name', 'brand', 'quantity', 
                                                'expiry', 'unit'])
    item_id = request.form.get('item_id')
    name = sanitised_fields[0]
    brand = sanitised_fields[1]
    quantity = sanitised_fields[2]
    expiry_date = sanitised_fields[3]
    unit = sanitised_fields[4]
    barcode = request.form.get('barcode')
    if barcode == "None":
        barcode = None
    # Checks that the format is correct for the expiry date.
    valid = input_handling.validate_expiry(expiry_date)
    valid = input_handling.validate_expiry(expiry_date)
    if not valid:
         return jsonify({'success': False, 'error': "Expiry formatted incorrectly"}), 400
    result = item.update_item(item_id, barcode, name, brand, expiry_date, quantity, unit)
    if not result.get("success"):
        return jsonify(result), 500

    # gets image if uploaded otherwise equals none
    image = request.files.get("item_image")
    # adds image if uploaded
    item.add_item_image(image, item_id)
    # item id does not need to be returned
    return jsonify({"success": True})
    
# Adds a new item to the database.
@app.route('/admin/item_view/add_item', methods = ['POST'])
@admin_only
def add_item_admin(): 
    # Sanitise the input to prevent sql injection.
    sanitised_fields = input_handling.sanitise_all(['barcode', 'name', 'brand', 'quantity', 
                                                'expiry', 'unit'])
    barcode = sanitised_fields[0]
    name = sanitised_fields[1]
    brand = sanitised_fields[2]
    quantity = sanitised_fields[3]
    expiry_date = sanitised_fields[4]
    unit = sanitised_fields[5]
    if barcode == "":
        barcode = None
    # Checks that the format is correct for the expiry date.
    valid = input_handling.validate_expiry(expiry_date)
    if not valid:
         return jsonify({'success': False, 'error': "Expiry formatted incorrectly"}), 400
    result = item.add_item(barcode, name, brand, expiry_date, quantity, unit)
    if not result.get("success"):
        return jsonify(result), 500
    
    item_id = result.get("item_id")
    # gets image if uploaded otherwise equals none
    image = request.files.get("item_image")
    # adds image if uploaded
    item.add_item_image(image, item_id)
    # item id does not need to be returned
    return jsonify({"success": True})

# Updates the details of a selected recipe in the recipe table.
@app.route('/admin/recipe_view/update_recipe', methods = ['POST'])
@admin_only
def update_recipe_admin():
    # Sanitise the input to prevent sql injection.
    sanitised_fields = input_handling.sanitise_all(['name', 'instructions', 
                                                'prep', 'cook', 'servings'])
    name = sanitised_fields[0]
    instructions = sanitised_fields[1]
    recipe_id = request.form.get('recipe-id')
    prep = sanitised_fields[2]
    cook = sanitised_fields[3]
    servings = sanitised_fields[4]
    result = admin_recipe.update_recipe(recipe_id, name, servings, prep, cook, instructions)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)
    
# Adds the details of a selected recipe in the recipe table.
@app.route('/admin/recipe_view/add_recipe', methods = ['POST'])
@admin_only
def add_recipe_admin():
    # Sanitise the input to prevent sql injection.
    sanitised_fields = input_handling.sanitise_all(['name', 'instructions', 
                                                'prep', 'cook', 'servings'])
    name = sanitised_fields[0]
    instructions = sanitised_fields[1]
    prep = sanitised_fields[2]
    cook = sanitised_fields[3]
    servings = sanitised_fields[4]
    result = admin_recipe.add_recipe(name, servings, prep, cook, instructions)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)
    
@app.route('/admin/recipe_view/update_recipe_ingredients', methods=['POST'])
@admin_only
def update_recipe_ingredients():
    # Requests lists since the rows are dynamically generated.
    names = request.form.getlist('name[]')
    units = request.form.getlist('unit[]')
    quantities = request.form.getlist('quantity[]')
    recipe_id = request.form.get('recipe-id')

    result = admin_recipe.update_recipe_ingredients(recipe_id, names, units, quantities)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)

@app.route('/admin/recipe_view/add_recipe_ingredients', methods=['POST'])
@admin_only
def add_recipe_ingredients():
    # Requests lists since the rows are dynamically generated.
    names = request.form.getlist('name[]')
    units = request.form.getlist('unit[]')
    quantities = request.form.getlist('quantity[]')
    recipe_id = request.form.get('recipe-id')

    result = admin_recipe.add_recipe_ingredients(recipe_id, names, units, quantities)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)

@app.route('/admin/recipe_view/recipe_id/', methods=['GET'])
@admin_only
def get_recipe_id():
    result = admin_recipe.get_id()
    if not result.get("success"):
        return jsonify(result), 500
    id = result.get("id")
    return jsonify(id)

@app.route('/admin/recipe_view/update_recipe_tools', methods=['POST'])
@admin_only
def update_recipe_tools():
    tool_ids = request.form.getlist('tools[]')
    recipe_id = request.form.get('recipe-id')
    result = admin_recipe.update_recipe_tools(recipe_id, tool_ids)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)
    
@app.route('/admin/recipe_view/add_recipe_tools', methods=['POST'])
@admin_only
def add_recipe_tools():
    tool_ids = request.form.getlist('tools[]')
    recipe_id = request.form.get('recipe-id')
    result = admin_recipe.add_recipe_tools(recipe_id, tool_ids)
    if not result.get("success"):
            return jsonify(result), 500
    return jsonify(result)


# Shopping List Interface Route

@app.route('/shopping_list', methods=['GET', 'POST'])
@user_only
def get_shoppingList():
    user_id = current_user.id
    # check the user request and performs action accordingly
    if request.method == 'POST':
        if 'clear' in request.form:
            result = shopping.clear_items(user_id)
        elif 'remove' in request.form:
            item_id = request.form.get('remove')
            result = shopping.remove_item(user_id, item_id)  
        elif 'mark_bought' in request.form:
            item_id = request.form.get('mark_bought')
            bought_str = request.form.get('bought')
            if bought_str is None:
                return jsonify({"success": False, "message": "Missing 'bought' status"}), 400
            bought = int(bought_str)
            result = shopping.item_bought(user_id, item_id, bought)
        
        if not result.get("success"):
            return jsonify(result), 500
        return jsonify(result)
    
    item_result = shopping.get_items(user_id)
    if not item_result.get("success"):
        return jsonify(result), 500
    items = item_result.get("items")
    # split items into bought and unbough lists
    unbought_items = [item for item in items if item[3] == 0]
    bought_items = [item for item in items if item[3] == 1]

    #check low stock items  in inventory and store them in variable 
    low_stock_result = shopping.low_stock_items(user_id)
    if not low_stock_result.get("success"):
        return jsonify(result), 500
    low_stock = low_stock_result.get("items")
    return render_template("shoppinglist.html", items=items, unbought_items=unbought_items, bought_items=bought_items, low_stock=low_stock)

# add items to shopping list
@app.route('/shopping_list/add', methods=['POST'])
@user_only
def add_shopping_item():
    user_id = current_user.id
    item_name = request.form.get('item_name')
    quantity = request.form.get('quantity')
    result = shopping.add_item(user_id, item_name, quantity)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)

# editing shopping list items
@app.route('/shopping_list/update', methods=['POST'])
@user_only
def update_shopping_item():
    user_id = current_user.id
    item_id = request.form.get('item_id')
    item_name = request.form.get('item_name')
    quantity = request.form.get('quantity')
    result = shopping.update_item(user_id, item_id, item_name, quantity)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)
    
# adding multipe shopping items at once, used for recipe system
@app.route("/shopping_list/add_multi", methods=["POST"])
@user_only
def add_shopping_items():
    user_id = current_user.id
    items_string = request.form.get("items")
    items = json.loads(items_string)
    if not (items):
        return jsonify({"success": False, "error": "No items selected."})
    
    result = shopping.add_items(user_id, items)
    if not result.get("success"):
        return jsonify(result), 500
    return jsonify(result)


### UTENSILS AND APPLIANCE SELECTION ROUTES
    
@app.route('/tools/select')
@user_only
def select_tools():
    user_id = current_user.id
    result = tool.get_tools("utensil")
    if not result.get("success"):
        return jsonify(result), 500
    utensils = result.get("tools")

    result = tool.get_tools("appliance")
    if not result.get("success"):
        return jsonify(result), 500
    appliances = result.get("tools")

    result = tool.get_user_tool_ids(user_id)
    if not result.get("success"):
        return jsonify(result), 500
    tool_ids = result.get("ids")

    return render_template('select_utensils.html', utensils=utensils, appliances=appliances, selected_ids=tool_ids)

@app.route('/tools/save', methods=['POST'])
@user_only
def save_tools():
    user_id = current_user.id
    selected_tools = request.form.getlist('tool')
    result = tool.save_user_tools(user_id, selected_tools)
    if not result.get("success"):
        return jsonify({"success": False, "message": "Failed to save tools."}), 500
    return jsonify({"success": True, "message": "Tools saved successfully!"})

@app.route("/tools/get")
@user_only
def get_tools():
    result = tool.get_tools()
    if not result.get("success"):
        return jsonify(result), 500
    tools = result.get("tools")
    return jsonify({"success": True, "tools": tools})


####    RECIPE ROUTES

@app.route("/recipes")
@user_only
def recipe_page():
    return render_template("recipes.html")

@app.route("/recipes/get", methods=["POST"])
@user_only
def get_recipes():
    user_id = current_user.id
    result = tool.get_user_tool_ids(user_id)
    if not result.get("success"):
        return jsonify(result), 500
    user_tool_ids = result.get("ids")

    search_term = request.form.get("search_term")
    page = request.form.get("page")

    personal_only = request.form.get("personal_only") == "on"
    allow_missing_items = request.form.get("missing_items") == "on"
    allow_insufficient_items = request.form.get("insufficient_items") == "on"
    allow_missing_tools = request.form.get("missing_tools") == "on"

    result = recipe_sql.get_recipes(search_term, page, user_id, personal_only)
    if not result.get("success"):
        return jsonify(result), 500
    recipes = result.get("recipes")

    filtered = []
    # for each recipe record returned from database
    for record in recipes:
        result = recipe_processing.create(record)
        if not result.get("success"):
            return jsonify(result), 500
        recipe_object = result.get("recipe")

        is_missing_tools = recipe_processing.calculate_missing_tools(recipe_object, user_tool_ids)
        # stops recipes with missing tools if theyre not allowed
        if not allow_missing_tools and is_missing_tools:
            continue

        result = recipe_processing.find_items_in_inventory(recipe_object, user_id, allow_insufficient_items, allow_missing_items)
        if not result.get("success"):
            return jsonify(result), 500

        # if filters didnt allow recipe
        if not result.get("allowed"):
            continue
        
        filtered.append(recipe_object)
    
    print([r.get("name") for r in filtered])
    # sorts recipe by how many soon to expire items it uses
    filtered.sort(key=lambda x: x["sort_value"])
    print([r.get("name") for r in filtered])
    
    return jsonify({"success": True, "recipes": filtered})
    
@app.route("/recipes/get/<recipe_id>")
@user_only
def get_recipe(recipe_id):
    user_id = current_user.id

    result = tool.get_user_tool_ids(user_id)
    if not result.get("success"):
        return jsonify(result), 500
    user_tool_ids = result.get("ids")

    result = recipe_sql.get_recipe(recipe_id)
    if not result.get("success"):
        return jsonify(result), 500
    record = result.get("recipe")

    result = recipe_processing.create(record)
    if not result.get("success"):
        return jsonify(result), 500
    recipe_object = result.get("recipe")

    recipe_processing.calculate_missing_tools(recipe_object, user_tool_ids)

    result = recipe_processing.find_items_in_inventory(recipe_object, user_id)
    if not result.get("success"):
        return jsonify(result), 500
    
    return jsonify({"success": True, "recipe": recipe_object})


@app.route("/recipes/add", methods=["POST"])
@user_only
def add_recipe():
    user_id = current_user.id
    # processes form and executes add function
    result = recipe_sql.process_form(recipe_sql.add_recipe, request.form, user_id)
    if not result.get("success"):
        if result.get("error") == "An internal error occurred.":
            return jsonify(result), 500
        return jsonify(result), 400
    return jsonify(result)

@app.route("/recipes/update", methods=["POST"])
@user_only
def update_recipe():
    user_id = current_user.id
    # processes form and executes update functions
    result = recipe_sql.process_form(recipe_sql.edit_recipe, request.form, user_id)
    if not result.get("success"):
        if result.get("error") == "An internal error occurred.":
            return jsonify(result), 500
        return jsonify(result), 400
    return jsonify(result)

@app.route("/recipes/delete/<recipe_id>")
@user_only
def remove_recipe(recipe_id):
    user_id = current_user.id
    result = recipe_sql.remove_recipe(recipe_id, user_id)
    if not result.get("success"):
        return jsonify(result), 500
    return result

if __name__ == '__main__':
    # Runs the app
    app.run()

