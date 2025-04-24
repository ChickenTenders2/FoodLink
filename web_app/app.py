## general imports for flask setup
from flask import Flask, jsonify, render_template, request, url_for, Response, redirect, session, flash
from flask_bootstrap import Bootstrap
import os

## shared operations for user and admin:
# for scanning items (barcode or ai object recogniser)
from scanner import Scanner
# for checking item image exists
from os.path import isfile as file_exists

from tool import Tool
from item import Item

## user operations
from inventory import Inventory
from notification import notification
# for getting temperature and humidity of fridge
from thingsboard import thingsboard
#from success import Success
from shoppingList import shoppingList
# for recipe handling
from recipe import Recipe
from recipe_object import recipe_object
# for parsing ingredients and tools list of lists as string
import json

## admin operations
# for admin, item and recipe view
from admin_recipe import admin_recipe
from input_handling import InputHandling

from report import Report

### for login systems
# general flask login functions
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
# for email verification
from flask_mail import Mail
from email_verification import send_verification_code
# for user lockout after too many attempts
from time import time as current_time
# for validating password complexity (regular expression checker)
from re import search as re_search
# for encrypting password
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
# for accessing database
from models import User, Admin
# login forms
from applogin import LoginForm, CreateAccountForm, CombinedResetForm, ResetPasswordForm, AdminCreateForm, AdminPasswordForm
from extensions import db, login_manager

# Import database and user model
app = Flask(__name__, template_folder = "templates")

app.config["SESSION_PERMANENT"] = False     
app.config["SESSION_TYPE"] = "filesystem"

# Initialize Flask-Session
Session(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://FoodLink:Pianoconclusiontown229!@81.109.118.20/FoodLink'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'foodlink2305@gmail.com'  
app.config['MAIL_PASSWORD'] = 'fmgz nrxz mwul nqju'    
app.config['MAIL_DEFAULT_SENDER'] = 'FoodLink <foodlink2305@gmail.com>'

# Import and register the settings blueprint
from settings import settings_bp
app.register_blueprint(settings_bp)

# Initialize extensions
bootstrap = Bootstrap(app)
login_manager.init_app(app)
login_manager.login_view = 'login'  # This ensures users are redirected to login when needed
db.init_app(app)
mail = Mail(app)


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
                advanced_privileges=False
            )
            db.session.add(new_admin)
            db.session.commit()
            flash("New admin added successfully!", "success")
            return redirect(url_for('AdminDashboard'))

    return render_template("admin_add.html", form=form, message=message)

@app.route("/admin/update-password", methods=["GET", "POST"])
@admin_only
def AdminUpdatePassword():
    form = AdminPasswordForm()
    message = None

    if form.validate_on_submit():
        if not check_password_hash(current_user.password, form.current_password.data):
            message = "Current password is incorrect."
        elif form.new_password.data != form.confirm_password.data:
            message = "New passwords do not match."
        else:
            current_user.password = generate_password_hash(form.new_password.data)
            db.session.commit()
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
                    #flash("You were successfully logged in!")
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
                    db.session.add(user)
                    db.session.commit()
                    
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
                db.session.commit()

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
    # Check if email is already verified
    if current_user.email_verified:
        flash('Your email is already verified.', 'info')
        return redirect(url_for('email_verification_page'))
    
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
        return redirect(url_for('email_verification_page'))
    
    if stored_code == entered_code:
        # Code matches, update verification status
        current_user.email_verified = True
        db.session.commit()
        
        # Clear the code
        session["verification_codes"].pop(current_user.email, None)
        session.modified = True
        
        flash('Your email has been verified successfully!', 'success')
    else:
        flash('Invalid verification code. Please try again.', 'danger')
    
    return redirect(url_for('email_verification_page'))


### SETTINGS PAGE ROUTE

@app.route('/settings')
@user_only
def settings_page():
    return redirect(url_for('settings.settings_page'))

# @app.route('/success')
# def added_successfully():
#   try:
#     # Triggers the success alert function when the route is fetched
#     # so that the Raspberry Pi LCD updates with the message 'Added!'.
#     success.alert()
#     return jsonify({"success": True})
#   except Exception as e:
#         return jsonify({"success": False, "error": str(e)})

#### USER DASHBOARD ROUTES

@app.route('/dashboard', methods=['GET', 'POST'])
@user_only
def dashboard():

    temp_url = "https://thingsboard.cs.cf.ac.uk/dashboard/9c597b10-0b04-11f0-8ef6-c9c91908b9e2?publicId=0d105160-0daa-11f0-8ef6-c9c91908b9e2" 
    humid_url = "https://thingsboard.cs.cf.ac.uk/dashboard/74d87180-0dbc-11f0-8ef6-c9c91908b9e2?publicId=0d105160-0daa-11f0-8ef6-c9c91908b9e2"

    return render_template('index.html', temp_url=temp_url, humid_url = humid_url) #, notifications=notifications, unread_count=unread_count)

@app.route('/notification/mark_read', methods=['POST'])
@user_only
def mark_read_notification():
    try:
        notif_id = request.json.get('notif_id')
        if not notif_id:
            return jsonify({'success': False, 'error': 'Notification ID missing'}), 400
        else:
            notif.mark_read(notif_id)
            return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.context_processor
def inject_notifications(): 
    if current_user.is_authenticated: 
        try: 
            user_id = current_user.id
            notif.temperature_humidity_notification(user_id, None, None) 
            notif.expiry_notification(user_id) 
            notifications = notif.get_notifications(user_id) 
            unread_count = sum(1 for n in notifications if n[4] == 0) 
            return dict(notifications=notifications, unread_count=unread_count) 
        except Exception as e: 
            print("[Context Processor Error]", e) 
            return dict(notifications=[], unread_count=0)
    else:
        return dict(notifications=[], unread_count=0)

# Dynamtically update notification bar
@app.route('/get_notifications', methods=['GET', 'POST']) 
@user_only
def get_notifications():
    try:
        device_id = "15b7a650-0b03-11f0-8ef6-c9c91908b9e2"
        user_id = current_user.id

        token = tb.get_jwt_token()
        data = tb.get_telemetry(token, device_id)

        temperature = humidity = None
        if data:
            temperature = float(data['temperature'][0]['value'])
            humidity = float(data['humidity'][0]['value'])

        notif.temperature_humidity_notification(user_id, temperature, humidity)
        notif.expiry_notification(user_id)

        notifications = notif.get_notifications(user_id)
        unread_count = sum(1 for n in notifications if n[4] == 0)

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
    except Exception as e:
        print('[DEBUG]' , e)
        return jsonify({'success': False, 'error': str(e)})
  
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
    try:
        # searches for an item if query is provided otherwise gets all items
        if search_query:
            items = inventory.search_items(user_id, search_query)
        else:
            items = inventory.get_items(user_id)

        return jsonify({"success": True, 'items': items})
    except Exception as e:
        return jsonify({"success": False, "error":str(e)})

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
    response = inventory.process_add_form(user_id, item_id, request.form)    
    return jsonify(response)

# Update quantity and expiry of item in inventory
@app.route('/inventory/update_item', methods = ['POST'])
@user_only
def update_item(): 
    try:
        # gets variables needed to update item
        inventory_id = request.form['inventory_id']
        quantity = request.form['quantity']
        expiry_date = request.form['expiry_date']
        
        # Update the database with new quantity and expiry date
        inventory.update_item(inventory_id, quantity, expiry_date)
        # returns response to js code
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/remove_item', methods=['POST'])
@user_only
def remove_item():
    try:
        inventory_id = request.form['inventory_id']
        print("Inventory ID received:", request.form['inventory_id'])
        inventory.remove_item(inventory_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route("/inventory/add_item/new", methods = ["POST"])
@user_only
def new_item():
    user_id = current_user.id
    response = item.process_add_form(request.form, user_id)
    item_id = response["item_id"]

    # if the item was not succesffuly added to the item table
    if not response["success"]:
        return jsonify(response)
    else:
        # gets image if uploaded otherwise equals none
        image = request.form.get("item_image", None)
        original_item_id = request.form.get("item_id") or None
        # adds image if uploaded or uses cloned image if possible
        item.add_item_image(image, item_id, original_item_id)
    
    if not request.form.get("add_to_inventory"):
        return jsonify({"success": True, "item_id": item_id, "message": "Item added to personal items."})
    
    response = inventory.process_add_form(user_id, item_id, request.form)
    if response["success"]:
        return jsonify({"success": True, "item_id": item_id, "message": "Item added to inventory and personal items."})
    else:
        return jsonify(response)
    
@app.route("/inventory/update_items_quantity", methods=["POST"])
@user_only
def update_quantities():
    try:  
        items_used_string = request.form.get("items_used")

        # list variables must be stringified client side so lists transfer correctly
        # they are so decoded to get original data type back
        items_used = json.loads(items_used_string)

        if not (items_used):
            return jsonify({"success": False, "error": "no items added."})

        # performs updates function (set to amount or removes if quantity <= 0)
        inventory.update_quantities(items_used)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})



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

# Returns the barcode number if one is found
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
        return jsonify({"success":True})
    elif value =="false":
        scanner.toggle_mode(False)
        return jsonify({"success":True})
    else:
        return jsonify({"success":False})


### ITEM ROUTES ###

@app.route("/items/single_text_search/<item_name>")
@user_only
def single_item_search(item_name):
    user_id = current_user.id
    try:
        items = item.text_search(user_id, item_name)
        item_info = items[0]
        return jsonify({"success": True, "item": item_info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Get items by text search
@app.route("/items/text_search", methods=["POST"])
@user_only
def text_search():
    user_id = current_user.id
    try:
        search_term = request.form["search_term"]
        items = item.text_search(user_id, search_term)
        return jsonify({"success": True, "items": items})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Get item by barcode search
@app.route("/items/barcode_search/<barcode>")
@user_only
def get_item_by_barcode(barcode):
    user_id = current_user.id
    try:
        item_info = item.barcode_search(user_id, barcode)
        if item_info:
            # returns the first item in the list as barcodes are unique
            return jsonify({"success": True, "item": item_info})
        else:
            return jsonify({"success": False, "error": "Item not found."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Get item by id
@app.route("/items/get_item/<item_id>")
@user_only
def get_item(item_id):
    try:
        item_info = item.get_item(item_id)
        return jsonify({"success": True, "item": item_info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Add item interface
@app.route('/items/add_item')
@admin_only
def add_item():
    return render_template("add_item.html")

# Add item to item table
@app.route('/items/add_item/add', methods=["POST"])
@admin_only
def append_item_db():
    response = item.process_add_form(request.form)
    if response["success"]:
        item_id = response["item_id"]
        # gets image if uploaded otherwise equals none
        image = request.form.get("item_image", None)
        # adds image if uploaded
        item.add_item_image(image, item_id)
    
        # item id does not need to be returned
        return jsonify({"success": True})
    else:
        return jsonify(response)

# Check if item has an image
@app.route("/find_image/<item_id>")
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
    try:
        new_item_id = request.form.get("new_item_id")
        item_id = request.form.get("item_id") or None
        report.add_report(new_item_id, item_id, user_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error":str(e)})

@app.route("/items/reports")
@admin_only
def display_reports():
    return render_template("reports.html")

@app.route("/items/reports/get")
@admin_only
def get_reports():
    return jsonify({"success": True, "reports": report.get_reports()})

@app.route("/items/reports/<new_item_id>/<item_id>")
@admin_only
def display_report(new_item_id, item_id):
    return render_template("report.html", new_item_id = new_item_id, item_id = item_id)

@app.route("/items/reports/resolve", methods=["POST"])
@admin_only
def resolve_report():
    try:
        action = request.form.get("action")
        barcode = request.form.get("barcode") or None
        new_item_id = request.form.get("new_item_id")
        original_item_id = request.form.get("item_id") or None
        # gets image if uploaded otherwise equals none
        image = request.form.get("item_image", None)
        # if the missing item reported isnt elligible for being added 
        if action == "deny" and original_item_id is None:
            # gets the reports
            reports = report.get_reports_by(new_item_id)
            # report will be singular
            _, personal_item_name, user_id = reports[0]
            # removes the report
            report.remove_report(new_item_id)
            # notification message
            message = lambda item_name : f"""Thank you for reporting the missing item, {item_name}. 
                        Unfortunately, your item is not currently elligible to be added at this time.
                        However, you can still continue to use your personal item. 
                        """

            # notify user of the change
            notif.support_notification(user_id, message(personal_item_name))

            return jsonify({"success": True})
        # if the proposed error was with an item having incorrect information (misinformation)
        if original_item_id:
            # if the original item had an error
            if action == "approve":
                # updates original item with correct information if approved
                # sets the user_id = null for the item so it appears for all users
                item.process_update_form(original_item_id, request.form)
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
            duplicate_reports = report.get_reports_by(new_item_id, original_item_id, "id")

        # if the error was a missing item and it got approved
        else:
            # adds the missing item to the table
            # sets the user_id = null for the item so it appears for all users
            response = item.process_add_form(request.form)
            # gets the id to replace the personal items with
            replace_id = response["item_id"]

            # adds image if uploaded or uses users personal item image if possible
            item.add_item_image(image, replace_id, new_item_id)
    
            # notification message
            message = lambda item_name : f"""Thank you for reporting the missing item, {item_name}.
                        Your request has been approved!
                        Your personal item has been successfully replaced."""

            # find other reports that reported the missing item
            # finds by same barcode as their is no original item for missing items
            # also searches using the new_item_id incase the item has no barcode
            duplicate_reports = report.get_reports_by(new_item_id, barcode, "barcode")

        # gets the limit that a users item can have for quantity
        default_quantity = item.get_default_quantity(replace_id)
        # for each report of an item
        for personal_item_id, personal_item_name, user_id in duplicate_reports:
            # replace the personal item the user made with the now corrected / new item
            inventory.correct_personal_item(personal_item_id, replace_id, default_quantity)
            # removes the users personal item as it is no longer needed
            item.remove_item(personal_item_id)
            # removes the report
            report.remove_report(personal_item_id)
            # notify user of the change
            notif.support_notification(user_id, message(personal_item_name))

        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    

#### ADMIN VIEW ITEMS AND RECIPES ROUTES

# Item table interface
@app.route('/admin/item_view')
@admin_only
def get_items():
    # Splits the list of items into several pages.
    item_list = item.get_all()
    current_page = []
    items = []
    for index, row in enumerate(item_list, start = 1):
        if index % 30 == 0:
            items.append(current_page)
            current_page = []
        else:
            current_page.append(row)
    items.append(current_page)
    max = len(items) - 1
    return render_template("item_view.html", items = items[0], max = max)

# allows for no search query to be entered
@app.route('/admin/item_view/get', defaults={'search_query': None})
@app.route('/admin/item_view/get/<search_query>')
@admin_only
def search_items(search_query = None):
        # Checks if the search is for a specifc page.
        if search_query.isnumeric():
                item_list = item.get_all()
                current_page = []
                items = []
                # Splits the items so that 30 are displayed per page.
                for index, row in enumerate(item_list, start = 1):
                    if index % 30 == 0:
                        items.append(current_page)
                        current_page = []
                    else:
                        current_page.append(row)
                items.append(current_page)
                max = len(items) - 1
                # Renders the page with the given index query.
                return render_template("item_view.html", items = items[int(search_query)], max = max)
        else:
            # Searches for an item if query is provided otherwise gets all items.
            result = item.get_item_from_name(search_query)
            if result != [None]:
                return render_template("item_view_search.html", items = result)
            else:
                result = item.get_all()
                return render_template("item_view_search.html", items = [])
        
# Recipe table interface.
@app.route('/admin/recipe_view')
@admin_only
def admin_get_recipes():
    recipes = admin_recipe_sql.get_all()
    return render_template("recipe_view.html", recipes = recipes)

@app.route('/admin/recipe_view/add_item/<int:recipe_id>', methods=['GET'])
@admin_only
def get_ingredients(recipe_id):
    ingredients = recipe_sql.get_recipe_items(recipe_id)
    return jsonify(ingredients)

@app.route('/admin/recipe_view/get_tools_ids/<int:recipe_id>', methods=['GET'])
@admin_only
def get_tools_ids(recipe_id):
    tools = recipe_sql.get_recipe_tools(recipe_id)
    return jsonify(tools)

# Returns the tools as a dictionary so that names can be mapped to ids in the js code. 
@app.route('/admin/recipe_view/get_tools/', methods=['GET'])
@admin_only
def admin_get_tools():
    tools = tool.get_tools()
    tools = dict(tools)
    return jsonify(tools)

# Removes an item from the item table.
@app.route('/admin/item_view/delete', methods = ['POST'])
@admin_only
def delete_item():
    try:
        # Form data is formatted in utf-8 so it needs to be decoded.
        id = request.data.decode('utf-8')
        item.remove_item(id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
# Removes an item from the item table.
@app.route('/admin/recipe_view/delete', methods = ['POST'])
def delete_recipe():
    try:
        # Form data is formatted in utf-8 so it needs to be decoded since id was not submitted in a form.
        id = request.data.decode('utf-8')
        admin_recipe_sql.remove_recipe(id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Updates the details of a selected item in the item table.
@app.route('/admin/item_view/update_item', methods = ['POST'])
@admin_only
def update_item_admin(): 
    # Sanitise the input to prevent sql injection.
    sanitised_fields = input_check.sanitise_all(['name', 'brand', 'quantity', 
                                                'expiry', 'unit'])
    inventory_id = request.form['inventory_id']
    name = sanitised_fields[0]
    brand = sanitised_fields[1]
    quantity = sanitised_fields[2]
    expiry_date = sanitised_fields[3]
    unit = sanitised_fields[4]
    barcode = request.form['barcode']
    if barcode == "None":
        barcode = None
    # Checks that the format is correct for the expiry date.
    valid = input_check.validate_expiry(expiry_date)
    if valid:
        try:
            item.update_item(inventory_id, barcode, name, brand, expiry_date, quantity, unit)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    else:
         return jsonify({'success': False, 'error': str("Expiry formatted incorrectly")})
    
# Adds a new item to the database.
@app.route('/admin/item_view/add_item', methods = ['POST'])
@admin_only
def add_item_admin(): 
    # Sanitise the input to prevent sql injection.
    sanitised_fields = input_check.sanitise_all(['barcode', 'name', 'brand', 'quantity', 
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
    valid = input_check.validate_expiry(expiry_date)
    if valid:
        try:
            item.add_item(barcode, name, brand, expiry_date, quantity, unit)
            return jsonify({'success': True})
        except Exception as e:
            print(e)
            return jsonify({'success': False, 'error': str(e)})
    else:
         return jsonify({'success': False, 'error': str("Expiry formatted incorrectly")})

# Updates the details of a selected recipe in the recipe table.
@app.route('/admin/item_view/update_recipe', methods = ['POST'])
@admin_only
def update_recipe_admin():
    # Sanitise the input to prevent sql injection.
    sanitised_fields = input_check.sanitise_all(['name', 'instructions', 
                                                'prep', 'cook', 'servings'])
    name = sanitised_fields[0]
    instructions = sanitised_fields[1]
    recipe_id = request.form['recipe-id']
    prep = sanitised_fields[2]
    cook = sanitised_fields[3]
    servings = sanitised_fields[4]
    try:
        admin_recipe_sql.update_recipe(recipe_id, name, servings, prep, cook, instructions)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
# Adds the details of a selected recipe in the recipe table.
@app.route('/admin/item_view/add_recipe', methods = ['POST'])
@admin_only
def add_recipe_admin():
    # Sanitise the input to prevent sql injection.
    sanitised_fields = input_check.sanitise_all(['name', 'instructions', 
                                                'prep', 'cook', 'servings'])
    name = sanitised_fields[0]
    instructions = sanitised_fields[1]
    prep = sanitised_fields[2]
    cook = sanitised_fields[3]
    servings = sanitised_fields[4]
    try:
        admin_recipe_sql.add_recipe(name, servings, prep, cook, instructions)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/admin/item_view/update_recipe_ingredients', methods=['POST'])
@admin_only
def update_recipe_ingredients():
    try:
        # Requests lists since the rows are dynamically generated.
        names = request.form.getlist('name[]')
        units = request.form.getlist('unit[]')
        quantities = request.form.getlist('quantity[]')
        recipe_id = request.form['recipe-id']  

        admin_recipe_sql.update_recipe_ingredients(recipe_id, names, units, quantities)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/item_view/add_recipe_ingredients', methods=['POST'])
@admin_only
def add_recipe_ingredients():
    try:
        # Requests lists since the rows are dynamically generated.
        names = request.form.getlist('name[]')
        units = request.form.getlist('unit[]')
        quantities = request.form.getlist('quantity[]')
        recipe_id = request.form['recipe-id']  

        admin_recipe_sql.add_recipe_ingredients(recipe_id, names, units, quantities)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/recipe_view/recipe_id/', methods=['GET'])
@admin_only
def get_recipe_id():
    try:
        id = admin_recipe_sql.get_id()
        return jsonify(id)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/item_view/update_recipe_tools', methods=['POST'])
@admin_only
def update_recipe_tools():
    try:
        tool_ids = request.form.getlist('tools[]')
        recipe_id = request.form['recipe-id']  
        admin_recipe_sql.update_recipe_tools(recipe_id, tool_ids)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/admin/item_view/add_recipe_tools', methods=['POST'])
@admin_only
def add_recipe_tools():
    try:
        tool_ids = request.form.getlist('tools[]')
        recipe_id = request.form['recipe-id']  
        admin_recipe_sql.add_recipe_tools(recipe_id, tool_ids)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})



# Shopping List Interface Route

@app.route('/shopping_list', methods=['GET', 'POST'])
@user_only
def get_shoppingList():
    user_id = current_user.id
    if request.method == 'POST':
        try:
            if 'clear' in request.form:
                shop.clear_items(user_id)
                return jsonify({"success": True, "action": "clear"})
            elif 'remove' in request.form:
                item_id = request.form['remove']
                shop.remove_item(item_id)
                return jsonify({"success": True, "action": "remove", "item_id": item_id})
            elif 'mark_bought' in request.form:
                item_id = request.form['mark_bought']
                bought_str = request.form.get('bought', 0)
                bought = int(bought_str)
                shop.item_bought(item_id, bought)
                return jsonify({"success": True, "action": "mark_bought"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    
    items = shop.get_items(user_id)
    unbought_items = [item for item in items if item[3] == 0]
    bought_items = [item for item in items if item[3] == 1]

    low_stock = shop.low_stock_items(user_id)
    return render_template("shoppinglist.html", items=items, unbought_items=unbought_items, bought_items=bought_items, low_stock=low_stock)

@app.route('/shopping_list/add', methods=['POST'])
@user_only
def add_shopping_item():
    user_id = current_user.id
    try:
        item_name = request.form['item_name']
        quantity = request.form['quantity']
        shop.add_item(user_id, item_name, quantity)
        return jsonify({"success": True, "action": "add", "item": item_name})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/shopping_list/update', methods=['POST'])
@user_only
def update_shopping_item():
    try:
        item_id = request.form['item_id']
        item_name = request.form['item_name']
        quantity = request.form['quantity']
        shop.update_item(item_id, item_name, quantity)
        return jsonify({"success": True, "action": "update", "item": item_name})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/shopping_list/add_multi", methods=["POST"])
@user_only
def add_shopping_items():
    user_id = current_user.id
    try:
        items_string = request.form.get("items")
        items = json.loads(items_string)
        if not (items):
            return jsonify({"success": False, "error": "No items selected."})
        
        shop.add_items(user_id, items)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


### UTENSILS AND APPLIANCE SELECTION ROUTES
    
@app.route('/tools/select')
@user_only
def select_tools():
    user_id = current_user.id
    utensils = tool.get_tools("utensil")
    appliances = tool.get_tools("appliance")
    tool_ids = tool.get_user_tool_ids(user_id)
    return render_template('select_utensils.html', utensils=utensils, appliances=appliances, selected_ids=tool_ids)

@app.route('/tools/save', methods=['POST'])
@user_only
def save_tools():
    user_id = current_user.id
    try:
        selected_tools = request.form.getlist('tool')
        tool.save_user_tools(user_id, selected_tools)
        return jsonify({"success": True, "message": "Tools saved successfully!"})
    except Exception as e:
        print(e)
        return jsonify({"success": False, "message": "Failed to save tools."})

@app.route("/tools/get")
@user_only
def get_tools():
    tools = tool.get_tools()
    print(tools)
    return jsonify({"success": True, "tools": tools})

@app.route("/recipes")
@user_only
def recipe_page():
    return render_template("recipes.html")

@app.route("/recipes/get", methods=["POST"])
@user_only
def get_recipes():
    user_id = current_user.id
    try:
        ###### CURRENTLY GET TOOL IDS EACH TIME UPDATE WHEN SESSION MADE TO CHANGEO NLY AFTER TOOLS/SAVE
        user_tool_ids = tool.get_user_tool_ids(user_id)


        search_term = request.form.get("search_term")
        page = int(request.form.get("page"))

        print(search_term)
        personal_only = request.form.get("personal_only") == "on"
        allow_missing_items = request.form.get("missing_items") == "on"
        allow_insufficient_items = request.form.get("insufficient_items") == "on"
        allow_missing_tools = request.form.get("missing_tools") == "on"
        recipes = recipe_sql.get_recipes(search_term, page, user_id, personal_only)

        filtered = []
        # for each recipe record returned from database
        for record in recipes:
            recipe = recipe_object(record)
            recipe.calculate_missing_tools(user_tool_ids)
            recipe.find_items_in_inventory(user_id)

            # applies filters
            # if the filter referenced is true:
            # stops recipes with missing ingredients
            if not allow_missing_items and recipe.missing_ingredients:
                continue
            # stops recipes with insufficient ingredient quantities
            if not allow_insufficient_items and recipe.insufficient_ingredients:
                continue
            # stops recipes with missing tools
            if not allow_missing_tools and recipe.missing_tool_ids:
                continue

            filtered.append(recipe.to_dict())

        return jsonify({"success": True, "recipes": filtered})
    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e)})
    
@app.route("/recipes/get/<recipe_id>")
@user_only
def get_recipe(recipe_id):
    user_id = current_user.id
    try:
        record = recipe_sql.get_recipe(recipe_id)
        recipe = recipe_object(record)
        user_tool_ids = tool.get_user_tool_ids(user_id)
        recipe.calculate_missing_tools(user_tool_ids)
        recipe.find_items_in_inventory(user_id)
        recipe_dict = recipe.to_dict()
        return jsonify({"success": True, "recipe": recipe_dict})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/recipes/add", methods=["POST"])
@user_only
def add_recipe():
    user_id = current_user.id
    try:
        name = request.form.get("name")
        servings = request.form.get("servings")
        prep_time = request.form.get("prep_time")
        cook_time = request.form.get("cook_time")
        instructions = request.form.get("instructions")
        
        ingredients_string = request.form.get("ingredients")
        tool_ids_string = request.form.get("tool_ids")

        # list variables must be stringified client side so lists transfer correctly
        # they are so decoded to get original data type back
        ingredients = json.loads(ingredients_string)
        tool_ids = json.loads(tool_ids_string)

        if not (ingredients or tool_ids):
            return jsonify({"success": False, "error": "ingredients or tool were empty."})
        
        print(ingredients)
        print(tool_ids)

        # performs update functions
        #### WHEN REMOVING OOP MAKE SURE TO USE SINGLE CURSOR AND COMMIT FOR THESE FUNCTIONS
        recipe_id = recipe_sql.add_recipe(name, servings, prep_time, cook_time, instructions, user_id)
        print("added recipe")
        recipe_sql.edit_recipe_items(recipe_id, ingredients)
        print("updated recipe_items")
        recipe_sql.edit_recipe_tools(recipe_id, tool_ids)
        print("updated recipe_tools")

        return jsonify({"success": True, "recipe_id": recipe_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/recipes/update", methods=["POST"])
@user_only
def update_recipe():
    try:
        recipe_id = request.form.get("recipe_id")
        name = request.form.get("name")
        servings = request.form.get("servings")
        prep_time = request.form.get("prep_time")
        cook_time = request.form.get("cook_time")
        instructions = request.form.get("instructions")
        
        ingredients_string = request.form.get("ingredients")
        tool_ids_string = request.form.get("tool_ids")

        
        # list variables must be stringified client side so lists transfer correctly
        # they are so decoded to get original data type back
        ingredients = json.loads(ingredients_string)
        tool_ids = json.loads(tool_ids_string)

        if not (ingredients or tool_ids):
            return jsonify({"success": False, "error": "ingredients or tool were empty."})
        
        print(ingredients)
        print(tool_ids)

        # performs update functions
        #### WHEN REMOVING OOP MAKE SURE TO USE SINGLE CURSOR AND COMMIT FOR THESE FUNCTIONS
        recipe_sql.edit_recipe(recipe_id, name, servings, prep_time, cook_time, instructions)
        print("updated recipe")
        recipe_sql.edit_recipe_items(recipe_id, ingredients)
        print("updated recipe_items")
        recipe_sql.edit_recipe_tools(recipe_id, tool_ids)
        print("updated recipe_tools")

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/recipes/delete/<recipe_id>")
@user_only
def remove_recipe(recipe_id):
    try:
        ### MERGE FUNCTIONS WHEM REMOVING OOP
        recipe_sql.remove_recipe(recipe_id)
        recipe_sql.remove_recipe_items(recipe_id)
        recipe_sql.remove_recipe_tools(recipe_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    # Classes for handling sql expressions
    inventory = Inventory()
    item = Item()
    report = Report()
    # Class for handling barcode scanning
    scanner = Scanner()

    shop = shoppingList()

    #success = Success()

    # notification class instance
    notif = notification() 

    # thingsboard class instance
    tb = thingsboard()

    tool = Tool()

    recipe_sql = Recipe()

    input_check = InputHandling()

    admin_recipe_sql = admin_recipe()

    # Runs the app
    app.run(debug=True)

