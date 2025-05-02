FoodLink: Smart Fridge Assistant

### BRIEF DESCRIPTION OF THE SYSTEM AND ITS OBJECTIVES


Feature

### HIGHLIGHT OF KEY FEATURES


Technology Stack:

- **Frontend** : HTML, CSS, JavaScript
- **Backend** : Python (Flask Framework)
- **Database** : MariaDB
- **IoT Integration** : Thingsboard API


Installation:

## Prerequisites

- Raspberry Pi with Raspberry Pi OS
- Python 3.9+ and pip
- Virtualenv: `pip install virtualenv`
- Internet access
- Basic terminal and sudo access

---

## Extracting the Project from ZIP

Unzip the provided FoodLink project folder and navigate into it:

```bash
unzip FoodLink.zip
cd FoodLink
```

---

## Setting Up Python Virtual Environment

```bash
cd setup
virtualenv venv
source venv/bin/activate
```

---

## Installing Python Dependencies

```bash
pip install -r requirements.txt
```

---

## Setting Up MariaDB on Raspberry Pi

### 1. Install MariaDB

```bash
sudo apt update
sudo apt install mariadb-server -y
```

### 2. Secure the Installation

```bash
sudo mysql_secure_installation
```

Choose:
- Set root password
- Remove anonymous users
- Disallow remote root login
- Remove test database
- Reload privileges

---

### 3. Create User and Database

```bash
sudo mariadb
```

Inside the MariaDB prompt:

```sql
CREATE DATABASE foodlink_db;
CREATE USER 'foodlink_user'@'localhost' IDENTIFIED BY 'strongpassword';
GRANT ALL PRIVILEGES ON foodlink_db.* TO 'foodlink_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## Importing the Database (provided schema)

```bash
sudo mariadb -u foodlink_user -p foodlink_db < setup/foodlink_schema.sql
```

---

## Ensure MariaDB is Running

```bash
sudo systemctl status mariadb
```

If it is not active, start it using:

```bash
sudo systemctl start mariadb
```

---

## Configuring the Web App

Update DB config in your Flask code (e.g. `.env`):

```python
DB_USER = "foodlink_user"
DB_PASSWORD = "strongpassword"
DB_NAME = "foodlink_db"
```

---

## Running the Application

```bash
cd ../web_app
python app.py
```

Visit: `http://localhost:5000` in your browser.

---

## Final Notes

- Keep your Raspberry Pi connected to ThingsBoard for IoT features
- Default port is 5000; can be configured in `app.py`

Usage:

### HOW TO NAVIGATE THE WEBSITE AND USE FUNCTIONALITY

### 1. Login / Create Account

### 2. Email Verification

### 3. User Dashboard

### 4. Settings

### 5. Inventory

### 6. Add Items to Inventory (Manual, Barcode scanner, AI recognitions)

### 7. Report

### 8. Shopping List
- Click the Shopping List tile, or the Shopping List button in the Navigation bar.
- Click the 'Add Item' button to add items manually by entering the name and quantity.
- Click 'Add to Shopping List' to add items from suggestions.
- Mark items as bough by clicking '✔'.
- Remove items from list by clicking '🗑' or clicking the 'Clear Shopping List' to clear all items.

### 9. Notifications
- Click the 🔔 icon of the top right of the navigation bar to view unread notifications.
- Notifcation include:
    - Expiring Food
    - Fidge Temperature/Humidity
    - Support messages on reported items
- Click on notification to mark it as read.

### 10. Email Notification
- Enable via settings to recieve notifications when:
    - Items are about to expire or have expired.
    - Fridge temperature/humidity is abnormal.
    - Report has been resolved by admin.

### 11. Recipes

### 12. Admin Dashboard (Admin Only)

### 13. Item Management (Admin Only)

### 14. Recipe Managemnt (Admin Only)

### 15. Manage Report (Admin Only)

### 16. Create Admins (Admin Only)



# FoodLink Project Folder Structure
```
FoodLink/
    arduino/                                    # Arduino-related code     
        sensor_readings_to_bluetooth/           # Folder required to run the Raspberry Pi code in the IDE
            sensor_readings_to_bluetooth.ino    # Arduino C++ code for collecting temperature humidity and distance readings. These are sent to the Pi in JSON
                                                  string form using Bluetooth so that they are ready to be sent to ThingsBoard.

    raspberry_pi/                               # Code for fridge add-on raspberry pi     
        notify.py                               # Collects values for both the distance and message keys from ThingsBoard and uses them to check if the buzzer 
                                                  and LCD.

    setup/                                      # Files needed for setup  
        itemDB.py                               # Python script to insert items to item table.
        recipeDB.py                             # Inserts recipes into recipe table, recipe ingredients into recipe_items table and recipe utensils and appliance into recipe_tool table.
        requirements.txt                        # Python dependecies

    trained_AI_model/
        FoodLink.pt                             # Custom trained YOLOv8n object detection model.
        reference.bib                           # Bib file containing full references to the datasets that form the custom      
                                                  set.
        train.py                                # File used to train the YOLO model.    
         
    web_app/                                    # All files and folders for the web app.
        flask_session/                          # Stores flask session data in filesystem.

        static/     
            images/                             # Uploaded item images or icons        
                1.jpg                           # Example of image for item with id 1                                                                                         
                2.jpg                           # etc...    
                3.jpg
                ...
                notification_bell.png           # Notification icon   
                null.jpg                        # Placeholder image if item doesn't have one
               
            js/                                 # Frontend scripts  
                add_item.js
                barcode_scan.js
                inventory.js
                inventory_add.js
                item_handling.js
                item_view.js
                navbar.js                       # Collapses the navigation bar when the screen is minimised.
                notification.js                 # Handles the dynamic updating of the notification popup, updates number of unread notification in badge, chnages notification style when marked as read.
                recipes.js
                recipe_view.js
                report.js
                reports.js
                select_utensils.js
                settings.js
                shopping_list.js                # Handles form submissions, hides and displays add/edit popups, shows toast notification to confirm success.

            settings_style.css                  # Style sheet for settings page      
            style.css                           # Style sheet for all pages apart from settings        

        templates/                              # HTML templates (rendered by Flask) 
            add_item.html
            admin_add.html
            admin_base.html
            admin_dashboard.html
            admin_login.html
            admin_update_password.html
            base.html                           # Base layout used across all templates (navigation bar, contianer for flash messages, js scripts, styling sheets)
            createAccount.html
            email_verification.html
            index.html                          # User dashboard (diplays temp/humidity real time data, tiles to navugate to inventory, shopping list and recipes)
            inventory.html
            inventory_add.html
            item_view.html
            item_view_search.html
            login.html
            recipes.html
            recipe_view.html
            report.html
            reports.html
            resetByEmail.html
            resetPassword.html
            select_utensils.html
            settings.html
            shoppinglist.html                   # Shooping List UI (add/edit/remove/clear items)

        admin_recipe.py                         # Handles operations performed on the recipe database table when the admin recipe_view page is in use.
        alchemy_db.py                           # Loads sql alchemy with flask and handles safe execution of commands with error handling.
        app.py                                  # Main Flask app entry point. Docstrings, aided by comments explain the purpose of each function.
        database.py                             # Connects to the database using the envrionment variables set and acts as a single point to connect to the database (
                                                  for all sql commands using mariadb connector). Auto-reconnects on connection loss and handles rollbacks safely. on execute failure. Handles closing connection when server stops so connections don't build up on the database.
                                                  
        email_verification.py                   # Manages user email verification through verification.
                                                  codes, sending emails, and confirming user identity.
                                                  Made through Flask's Blueprint and Flask Mail, and render_template.
        flask_forms.py
        input_handling.py                       # Contains a function for validating date format as well as functions that sanitise inputs to prevent malicious 
                                                  SQl injection attacks. Both of these functions use the re module to achieve their goals.
        inventory.py                            # Handles basic CRUD sql commands for a users inventory, html form processing for adding an item to inventory,
                                                  formatting of expiry date for the front end, and more advanced sql commands: 
                                                  strict_search (used in recipe proccesing):         finds an item which is the best match for an ingredient
                                                  correct_personal_item (used in resolving reports): replaces a users personal item (with quantity checks) if their report gets approved.
                                                  
        item.py                                 # Handles sql commands for item table, image storing functionality, and form processing.
        models.py
        notification.py                         # Handles sql commands for notification table, temp/humidity notification cooldown, and email notifications.

        recipe.py                               # Handles recipe sql commands (CRUD), and html form processing for adding and editing a recipe.

        recipe_processing.py                    # Creates a "smart recipe object" which matches a recipe against a users tools and inventory, calculates missing  
                                                  tools, finds missing or insufficient quantity ingredients, and sorts recipes by which uses most soon to expire items (with weighting applied).

        report.py                               # Handles SQL operations for item errors: adding user report of an item, admin get all, find duplicate and remove report
                                                  (after resolving), admins can assign a report to themselves (with override checks)

        scanner.py                              # Processes users camera feed as a video and scans each frame using a barcode reader or AI object recogniser. based on the mode
        settings.py                             # Handles user preferences through multiple view classes.
                                                  that control account details and notification preferences. Made through Flask's Blueprint, MethodView,
                                                  Flask Login, and werkzeug.security for password hashing.
        shopping.py
        success.py                              # Publishes a message with the value 'Added' to ThingsBoard over secure MQTT using the tb_mqtt_client library. 
        thingsboard.py
        tool.py                                 # Handles tool SQL commands (CRUD)

    README.md                                   # Project README file (this file)
```