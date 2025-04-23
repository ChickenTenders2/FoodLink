from flask import Flask, jsonify, render_template, request, url_for, Response, redirect, session, flash
from inventory import Inventory
from scanner import Scanner
from item import Item
#from success import Success
from report import Report
from shoppingList import shoppingList
from os.path import isfile as file_exists
from notification import notification
from thingsboard import thingsboard
from tool import Tool
from recipe import Recipe
from recipe_object import recipe_object
import json
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from extensions import db, login_manager
from flask_mail import Mail, Message
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import os
import random
from models import User
from applogin import LoginForm, CreateAccountForm, CombinedResetForm, ResetPasswordForm
from email_verification import send_verification_code, verification_codes

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

# Initialize Flask-Login
login_manager = LoginManager(app)

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def back_to_login():
    return redirect('/login')

# Index route
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    else:
        # user is not logged in
        return redirect(url_for('login'))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get("user") is None:
        form = LoginForm()
        error = None
    
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()

            session["type"] = "client"
            if user is None or not check_password_hash(user.password, form.password.data):
                error = "Error: Invalid Credentials"
            else:
                login_user(user, form.remember_me.data)
                session["user_id"] = user.id

                # Check if email is verified
                if not user.email_verified:
                    flash("Please verify your email address to access all features.")
                    return redirect(url_for('email_verification_page'))
            
            return redirect(url_for('dashboard'))
    
        return render_template('login.html', form=form, error=error)
    else:
        return redirect(url_for('dashboard'))
    
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
                flash("Account created successfully! Please verify your email.")
                return redirect(url_for('email_verification_page'))
            else:
                msg = "Passwords mismatched." 
    return render_template('createAccount.html', form=form, msg=msg)


@app.route('/resetByEmail', methods=['GET', 'POST'])
def resetByEmail():
     
    form = CombinedResetForm()
    error = None

    if form.submit_email.data and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_verification_code(user, mail)
            flash("Verification code sent to your email.")
            error = "Verification code sent to your email."
        else:
            error = "Invalid email address."

    elif form.submit_otp.data and form.validate():
        user = User.query.filter_by(email=form.email.data).first()

        if user and verification_codes.get(user.email) == form.otp.data:
        
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

    return render_template('resetPassword.html', form=form, error=error)

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop("user_id", None)
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


# @app.route('/success')
# def added_successfully():
#   try:
#     # Triggers the success alert function when the route is fetched
#     # so that the Raspberry Pi LCD updates with the message 'Added!'.
#     success.alert()
#     return jsonify({"success": True})
#   except Exception as e:
#         return jsonify({"success": False, "error": str(e)})


# Dashboard Route
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    try:
        device_id = "15b7a650-0b03-11f0-8ef6-c9c91908b9e2"
        user_id = session.get("user_id")

        token = tb.get_jwt_token()
        data = tb.get_telemetry(token, device_id)
        temperature = humidity = None

        if data:
            temperature = float(data['temperature'][0]['value'])
            humidity = float(data['humidity'][0]['value'])


        notif.temperature_humidity_notification(user_id, temperature, humidity)
        notif.expiry_notification(user_id)
    except Exception as e:
        print("not connected to school wifi/vpn")

    temp_url = "https://thingsboard.cs.cf.ac.uk/dashboard/9c597b10-0b04-11f0-8ef6-c9c91908b9e2?publicId=0d105160-0daa-11f0-8ef6-c9c91908b9e2" 
    humid_url = "https://thingsboard.cs.cf.ac.uk/dashboard/74d87180-0dbc-11f0-8ef6-c9c91908b9e2?publicId=0d105160-0daa-11f0-8ef6-c9c91908b9e2"
    
    notifications = notif.get_notifications(user_id)
    unread_count = sum(1 for n in notifications if n[4] == 0)

    if request.method == 'POST' and request.json.get('mark_read'): 
        try: 
            notif_id = request.json.get('mark_read') 
            notif.mark_read(notif_id) 
            return jsonify({'success': True})
        except Exception as e: 
            return jsonify({'success': False, 'error': str(e)})

    return render_template('index.html', temp_url=temp_url, humid_url = humid_url, notifications=notifications, unread_count=unread_count)

# Dynamtically update notification bar
@app.route('/get_notifications', methods=['GET'])
def get_notifications():
    user_id = 2

    device_id = "15b7a650-0b03-11f0-8ef6-c9c91908b9e2"
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
  
### INVENTORY ROUTES ###

# Inventory interface
@app.route('/inventory/')
@login_required
def get_inventory():
    return render_template("inventory.html")

# allows for no search query to be entered
@app.route('/inventory/get/', defaults={'search_query': None})
@app.route('/inventory/get/<search_query>')
# used to dynamically get inventory
def api_inventory(search_query = None):
    user_id = session.get("user_id")
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
@login_required
def add_to_inventory():
    return render_template("inventory_add.html")

# Add item to inventory
@app.route("/inventory/add_item/add", methods=["POST"])
def append_inventory():
    user_id = session.get("user_id")
    item_id = request.form.get("item_id")
    response = inventory.process_add_form(user_id, item_id, request.form)    
    return jsonify(response)

# Update quantity and expiry of item in inventory
@app.route('/inventory/update_item', methods = ['POST'])
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
def remove_item():
    try:
        inventory_id = request.form['inventory_id']
        print("Inventory ID received:", request.form['inventory_id'])
        inventory.remove_item(inventory_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route("/inventory/add_item/new", methods = ["POST"])
def new_item():
    user_id = session.get("user_id")
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
def get_scanner():
    return Response(scanner.scan(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Closes camera module
@app.route('/scanner/close')
def close_scanner():
    scanner.release_capture()
    return jsonify({"success":True})

# Returns the barcode number if one is found
@app.route('/scanner/get_object')
def get_object():
    object = scanner.get_scanned()
    if (object):
        scanner.clear_scanned()
        return jsonify({"success": True, "object": object})
    else:
        return jsonify({"success": False})

@app.route("/unpause_scanner")
def unpause_scanner():
    scanner.unpause_scanner()
    return jsonify({"success":True})

@app.route("/scanner/toggle_mode/<value>")
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
def single_item_search(item_name):
    user_id = session.get("user_id")
    try:
        items = item.text_search(user_id, item_name)
        item_info = items[0]
        return jsonify({"success": True, "item": item_info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Get items by text search
@app.route("/items/text_search", methods=["POST"])
def text_search():
    user_id = session.get("user_id")
    try:
        search_term = request.form["search_term"]
        items = item.text_search(user_id, search_term)
        return jsonify({"success": True, "items": items})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Get item by barcode search
@app.route("/items/barcode_search/<barcode>")
def get_item_by_barcode(barcode):
    user_id = session.get("user_id")
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
def get_item(item_id):
    try:
        item_info = item.get_item(item_id)
        return jsonify({"success": True, "item": item_info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Add item interface
@app.route('/items/add_item')
def add_item():
    return render_template("add_item.html")

# Add item to item table
@app.route('/items/add_item/add', methods=["POST"])
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
def find_image(item_id):
    path = f"static/images/{item_id}.jpg"
    exists = file_exists(path)
    return jsonify({"success": exists})


### ITEM REPORT ROUTES

@app.route("/items/reports/new", methods=["POST"])
def report_item():
    user_id = session.get("user_id")
    try:
        new_item_id = request.form.get("new_item_id")
        item_id = request.form.get("item_id") or None
        report.add_report(new_item_id, item_id, user_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error":str(e)})

@app.route("/items/reports")
def display_reports():
    return render_template("reports.html")

@app.route("/items/reports/get")
def get_reports():
    return jsonify({"success": True, "reports": report.get_reports()})

@app.route("/items/reports/<new_item_id>/<item_id>")
def display_report(new_item_id, item_id):
    return render_template("report.html", new_item_id = new_item_id, item_id = item_id)

@app.route("/items/reports/resolve", methods=["POST"])
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


# Shopping List Interface Route

@app.route('/shopping_list', methods=['GET', 'POST'])
@login_required
def get_shoppingList():
    user_id = session.get("user_id")
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
def add_shopping_item():
    user_id = session.get("user_id")
    try:
        item_name = request.form['item_name']
        quantity = request.form['quantity']
        shop.add_item(user_id, item_name, quantity)
        return jsonify({"success": True, "action": "add", "item": item_name})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/shopping_list/update', methods=['POST'])
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
def add_shopping_items():
    user_id = session.get("user_id")
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
@login_required
def select_tools():
    user_id = session.get("user_id")
    utensils = tool.get_tools("utensil")
    appliances = tool.get_tools("appliance")
    tool_ids = tool.get_user_tool_ids(user_id)
    return render_template('select_utensils.html', utensils=utensils, appliances=appliances, selected_ids=tool_ids)

@app.route('/tools/save', methods=['POST'])
def save_tools():
    user_id = session.get("user_id")
    try:
        selected_tools = request.form.getlist('tool')
        tool.save_user_tools(user_id, selected_tools)
        return jsonify({"success": True, "message": "Tools saved successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to save tools."})

@app.route("/tools/get")
def get_tools():
    tools = tool.get_tools()
    print(tools)
    return jsonify({"success": True, "tools": tools})

@app.route("/recipes")
@login_required
def recipe_page():
    return render_template("recipes.html")

@app.route("/recipes/get", methods=["POST"])
def get_recipes():
    user_id = session.get("user_id")
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
def get_recipe(recipe_id):
    user_id = session.get("user_id")
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
def add_recipe():
    user_id = session.get("user_id")
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
def remove_recipe(recipe_id):
    try:
        ### MERGE FUNCTIONS WHEM REMOVING OOP
        recipe_sql.remove_recipe(recipe_id)
        recipe_sql.remove_recipe_items(recipe_id)
        recipe_sql.remove_recipe_tools(recipe_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


### SETTINGS PAGE ROUTE

@app.route('/settings')
@login_required
def settings_page():
    if current_user.is_authenticated:
        return redirect(url_for('settings.settings_page'))
    return redirect(url_for('login'))


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

    # Runs the app
    app.run(debug=True)

