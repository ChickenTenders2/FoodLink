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
        sensor_readings_to_bluetooth/
            sensor_readings_to_bluetooth.ino

    raspberry_pi/                               # Code for fridge add-on raspberry pi     
        notify.py

    setup/                                      # Files needed for setup  
        recipeDB.py
        requirements.txt

    web_app/                                    # All files and folders for the web app   
        static/     
            images/                             # Uploaded item images or icons        
                1.jpg                           # Example of image for item with id 1                                                                                         
                2.jpg                           # etc..    
                3.jpg
                notification_bell.png           # Notification icon   
                null.jpg                        # Placeholder image if item doesn't have one
               
            js/                                 # Frontend scripts  
                add_item.js
                barcode_scan.js
                inventory.js
                inventory_add.js
                item_handling.js
                item_view.js
                navbar.js
                notification.js
                recipes.js
                recipe_view.js
                report.js
                reports.js
                select_utensils.js
                settings.js
                shopping_list.js

            settings_style.css                  # Style sheet for settings page      
            style.css                           # Style sheet for all pages apart from settings        

        templates/                              # HTML templates (rendered by Flask) 
            add_item.html
            admin_add.html
            admin_base.html
            admin_dashboard.html
            admin_login.html
            admin_update_password.html
            base.html
            createAccount.html
            email_verification.html
            index.html
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
            shoppinglist.html

        admin_recipe.py
        alchemy_db.py                           # Loads sql alchemy with flask and handles safe execution of commands with error handling
        app.py                                  # Main Flask app entry point
        database.py
        email_verification.py
        flask_forms.py
        input_handling.py
        inventory.py
        item.py                                 # Handles sql commands for item table, image storing functionality, and form processing
        models.py
        notification.py
        recipe.py
        recipe_processing.py
        report.py
        scanner.py
        settings.py
        shopping.py
        success.py
        thingsboard.py
        tool.py
        yolov8s-worldv2.pt

    README.md                                   # Project README file (this file)
```

Backend Explanation:

### EXPLAIN FUNCTION HERE