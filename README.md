# FoodLink: Smart Fridge Assistant

FoodLink is a combined physical and web-based bespoke IoT platform with one main goal: reduce food waste. As an add-on, it provides an affordable and environmentally friendly way for consumers to achieve this goal. 

We have implemented various features to help us achieve a variety of objectives that help to contribute to our overall goal with efficiency and innovation:

- Item management system utilising the camera sensor to add items ---> Aids in the management of food inventory using visual computing features such as YOLO object detection trained on a custom dataset and barcode recognition and decoding.

- Recipe system and shopping list ---> Simplifies meal preparation by suggesting recipes based on items with the nearest average expiry and recommending items that are about to expire as shopping list additions as a convenient way to replenish food stocks.

- Virtual notifications and physical alerts ---> Prevents food spoilage using alerts (LCD update and buzzer sounds) for whether the door is left open for two minutes is triggered based on if the distance (calculated by an ultrasonic sensor) is greater than the distance from the door to the back of the fridge after this time. Notifications displayed on the website and sent by email remind users if items are about to expire as well as notifying them if the fridge conditions (calculated by a temperature and humidity sensor) are outside of a user-set optimal range. 

- Admin system ---> Full customer support with a reporting system that can help to swiftly fix any error in item information. Items and recipes can be edited using the admin account as an efficient alternative to manual database querying. 

To access the website, either run the project locally (not secure) following the steps below or access the website securely at:

https://foodlink-foodlink.apps.containers.cs.cf.ac.uk/

\* ThingsBoard API login requests appear to be blocked on OpenShift so the temperature and humidity notifications will not work when accessing the website online. 

Technology Stack:

- **Frontend** : HTML, CSS, JavaScript
- **Backend** : Python (Flask Framework)
- **Database** : MariaDB
- **IoT Integration** : Thingsboard API

# Installation:

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

### Importing the Database (provided schema)

```bash
sudo mariadb -u foodlink_user -p foodlink_db < setup/foodlink_schema.sql
```

---

### Ensure MariaDB is Running

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


# How to navigate and use the website:

### 1. Login / Create Account

Create account:
- Click on the first field to enter a username
- Click on the second field to enter an email address
- Click on the third field to enter a password that fits the format
- Re-enter the password in the fourth field(same as third field)
- Click on continue to create the account

Login:
- Click on the first field to enter your username
- Click on the second field to enter your password
- Click on continue to login
- If you are a new user, click on create account and it will redirect you to the create account page
- Click forgot password to reset your password

Reset Password:
- Press forgot password button
- Click on the first field to enter the email of the account you want to reset password on
- Click on send code button to receive the code for your email
- Enter the code in the second field
- Click on verify to redirect to forget password page
- Click on the first field to enter your new password
- Re-enter the password in the fourth field(same as first field)
- Click on continue to confirm the new password

### 2. Email Verification
- Click on Create Account
- Enter username, email, password, confirm the password 
- Once brought to the email verification page, click "Send Verification Code"
- Check email to receive code
- Paste code into field in email verification page, click "Verify Code"

### 3. User Dashboard
- Click on any button to access that page 

### 4. Settings
- Click on the "⚙️" menu on the navigation bar

Notification Settings:
- Click on the switch buttons to modify notification preferences and types
- Edit the number field to modify the temperature range settings
- Click on "Save Preferences" to save changes

My Account Settings:
- Click on either "Username" or "Name" fields, modify to change them (email is unchangable)
- Click on "Update Profile" to save changes

Delete Settings:
- Click on "Delete My Account"
- Enter account password

Privacy and Security Settings:
- Enter current password to "Current Password" field
- Enter new password into "New Password" and "Confirm New Password"
- Click on "Change Password" to save changes

### 5. Inventory
To update an item:
- Click on the item tile
- Edit the quantity or the expiry
- Click on save

To remove an item:
- Click on the item tile
- Click on the remove button

To search and sort the items:
- Enter the item names you want to find (optional)
- Click on sort drop down
- Click on a sort option
- Click apply

### 6. Add Items to Inventory (Manual, Barcode scanner, AI recognitions)
- When in the inventory, click 'Add Item'.

Adding Personal Items:
- Click 'Personal Items' to view items that you have created and only you can access. 
- Click on an item from the list to edit it.
- Click 'Add Item' to add the item to the inventory.
- Alternatively click 'Add Missing Item' to add an item that is not in your personal inventory
  or the items database and cannot be detected by the AI or barcode scanner methods.
- Complete each of the fields.
- Click 'Report Item' if you want admins to review the item that you added and potentially add
  add it to the system database. 

Barcode detection:
- This is the default scanning mode.
- Hold the barcode in front of the camera but keep the entire barcode within the frame.
- If an item is detected click 'Add Item' to add it to the inventory. 

AI Object Recognition (Experimental):
- Can currently detect Apples, Bananas, Oranges, Bell Peppers and Potatoes. We plan to further train the model
  to increase the accuracy of Orange detection.
- Check the box for AI Item Recognition.
- Hold the item close to the camera so the finer details are in view.
- If an item is detected click 'Add Item' to add it to the inventory.

- (NOTE: This mode is experimental and may not always be accurate. You can modify the fields before adding 
  the item in case of error. May need to adjust the angle of the item you are holding to gain more
  accurate results.)

Text Search:
- Click 'Add Missing Item' to open 'Add Personal Items'.
- Alternatively enter a search term in the search field and click on 'Search'.
- Select an item from the list of results.
- Verify that the quantity is correct and click 'Add Item' to add it to your inventory.

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
Add a recipe:
- Click on create new recipe
- Enter the name, servings, prep time, cook time, and instructions
- Click on edit ingredients button
- Click on add ingredients and fill in inputs
  (repeat until all ingredients are added)
- Click on save changes
- Click on edit tools buttons
- Select tool from dropdown 
- Click on add tool button 
  (repeat until all tools are added)
- Click on save recipe button

Clone a recipe:
- Select a public recipe
- Click on the clone button
- Repeat add recipe steps

Edit a personal recipe:
- Select a personal recipe
- Click on edit recipe button
- Repeat add recipe steps

Delete a personal recipe:
- Select a personal recipe
- Click on delete button
- Confirm delete

Create a recipe:
- Select a recipe
- Click on the create recipe button
- Change any of the quantity values as needed
- If subtitutions are required click on the remove button
- Click on add from inventory
- Click on an item which is not already added and in date
- Follow the last 2 steps for any additional ingredients aswell
- Update the quantity inputs of each to match the amount used
- Click on update inventory to update quantites and remove any fully used items

Filter and search recipes:
- Enter the search term
- Click on show filters button
- Select filters to apply
- Click on search

Add missing/insufficient ingredients to shopping list:
- Select a recipe
- Press shop insufficient items
- Deselect any items not needed
- Update quantities of any items needed
- Click on add selected

### 12. Admin Dashboard (Admin Only) 
- Log in as an existing admin 
- Actions in dashboard include:
    - Manage reports
    - Add new item
    - View item table
    - View recipe table
    - Add new admin
    - Change my password

### 13. Item Management (Admin Only)
- Sign in as an admin
- Click add new item button to add new item
- Click view item table to see all products
    - Use search bar to find specific items
    - Click edit in the item to edit it
    - Click delete to delete an icon
    
### 14. Recipe Managemnt (Admin Only)
- Sign in as admin
- Click View recipe table button to view all recipes
- CLick add to add a recipe
    - Add the name, instructions
    - Add ingredient, tools
- Click edit in a recipe to edit it
- Click delete in a recipe to delete it

### 15. Manage Report (Admin Only)
- Sign in as an admin
- Click manage reports button to see all unresolved issues
- Click in one of them to assign it to you
- Resolve report by adding item or updating existing item
- Sends user a notification
- Report disappears from queue once resolved

### 16. Create Admins (Admin Only)
- Log in as an existing admin with privileges
- Click the add new admin button
- Fill form
- Admin Added


# FoodLink Project Folder Structure

```
FoodLink/                                       # Project folder containing code for all components of the 
                                                  system.  

    ai_model_training_reference/
        reference.bib                           # Bib file containing full references to the datasets that form the custom      
                                                  set.
        train.py                                # File used to train the YOLO model.   
                     
    arduino/                                    # Arduino-related code     
        sensor_readings_to_bluetooth/           # Folder required to run the Arduino code in the IDE
            sensor_readings_to_bluetooth.ino    # Arduino C++ code for collecting temperature humidity and distance readings. 
                                                  These are sent to the Pi in JSON string form using Bluetooth so that they are 
                                                  ready to be sent to ThingsBoard.

    raspberry_pi/                               # Code for raspberry pi.     
        feedback.py                             # Collects values for both the distance and message keys from ThingsBoard and 
                                                  uses them to check if the buzzer and LCD need to be updated (if the door is left open 
                                                  for too long or if an item has been added to the user inventory).

    setup/                                      # Files needed for setup.
        foodlink_schema.sql                     # Database schema file for importing.

        itemDB.py                               # Python script to insert items to item table.

        recipeDB.py                             # Inserts recipes into recipe table, recipe ingredients into recipe_items table 
                                                  and recipe utensils and appliance into recipe_tool table.
<<<<<<< HEAD

    ai_model_training_reference/
        reference.bib                           # Bib file containing full references to the datasets that form the custom      
                                                  set.

        train.py                                # File used to train the YOLO model.    
         
=======
          
>>>>>>> 44b345979ac0e4646373ec8b348c72e2e1768c4c
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
                add_item.js                     # Handles the dynamic checking of item names / barcodes in the database and
                                                  enables the dynamic switching between scanning modes.

                inventory.js                    # Handles dynamic inventory operations using AJAX. Dynamically updates, remove and sorts items, as well as highlighting
                                                  items that are soon to expire.

                inventory_add.js                # Dynamically displays results from frame scan. Dynamic text search and item reports for missing items or items with 
                                                  misinformation. Calculates estimate of expiry date for each item. Dynamic CRUD operations for personal items, including 
                                                  cloning public items. Option to add any item to inventory, with quantity constraints.

                item_handling.js                # Handles some item functions which are shared between files. Dynamically gets image path, and updates image preview when 
                                                  file is uploaded. Gets each expiry value from an expiry time for processing.

                item_view.js                    # Handles the dynamic popup forms and transmission of data between the front back end 
                                                  AJAX (GET/POST) requests for efficient recipe modification.

                navbar.js                       # Collapses the navigation bar when the screen is minimised.

                notification.js                 # Handles the dynamic updating of the notification popup, updates number of 
                                                  unread notification in badge, chnages notification style when marked as read.

                recipes.js                      # Handles all dynamic features of recipes: adding a recipe, cloning a public recipe, edit personal (with cancel edit    
                                                  button) and removing a personal recipe. Allows for filters to be applied and seperates recipes by pages. Allows users 
                                                  to modify ingredient quantities, substitute ingredients and add additional ingredients before dynamically updating inventory. 
                                                  Dynamically adds missing/insufficient ingredients to the shopping list with options to change the quantity or remove ingredients 
                                                  that will be addded.

                recipe_view.js                  # As with item_view.js this file handles the dynamic popup forms and transmission 
                                                  of data between the front and back end AJAX (GET/POST) requests for efficient recipe 
                                                  modification.

                report.js                       # Handles displaying new item information, and original if error type was misinformation. Dynamically resolves report, before 
                                                redirecting back to main reports page.

                reports.js                      # Dynamically fills item table, and  handles sorting of reports. Also allows admins to dynamically assign reports to 
                                                  themselves with override checks.
                
                scanner.js                      # Gets the user's permission for access to the camera. Enables dynamic posting of 
                                                  frames as BLOB data to be analysed in the backend so that items and barcodes can be 
                                                  identified. Allows for dynamic and efficient switching between scanning scanning modes. 

                select_utensils.js              # Dynamically saves users utensils before redirecting to dashboard

                settings.js                     # Handles delete account popup
                
                shopping_list.js                # Handles form submissions, hides and displays add/edit popups, shows 
                                                  notification to confirm success.

            settings_style.css                  # Style sheet for settings page    

            style.css                           # Style sheet for all pages apart from settings        

        templates/                              # HTML templates (rendered by Flask) 
            add_item.html                       # Barcode scanner for admins to add new items efficiently

            admin_add.html                      # HTML layout for an admin adding a new admin

            admin_base.html                     # Navigation bar for admin pages

            admin_dashboard.html                # Admin dashboard

            admin_login.html                    # HTML layout for an admin to log in

            admin_update_password.html          # HTML layout for ad admin to change their password

            base.html                           # Base layout used across all templates (navigation bar, contianer for flash 
                                                  messages, js scripts, styling sheets)

            createAccount.html                  # Form to input sign up information with button to create account

            email_verification.html             # Options to send and enter email verification code

            index.html                          # User dashboard (diplays temp/humidity real time data, tiles to navigate to 
                                                  inventory, shopping list and recipes)

            inventory.html                      # Container for all items and form for searching applying filters

            inventory_add.html                  # UI with user camera footage and options buttons for item addition options.

            item_view.html                      # Database table UI for items with each row dynamically rendered using Jinja.

            item_view_search.html               # Database table UI for filtered items with each row dynamically rendered using Jinja.

            login.html                          # Handles inputs of user information for login, with forgot password and create new account options. Also allows admins to 
                                                  access admin login by pressing sign in text.

            recipes.html                        # Sets all the base popups and scrollable windows for recipe features mentioned in recipes.js

            recipe_view.html                    # Database table UI for recipes with each row dynamically rendered using Jinja.

            report.html                         # Shows single report and allows for admins to correct information, shows original item if applicable

            reports.html                        # Shows a table with all the reports and allows admins to assign a report to themselves

            resetByEmail.html                   # Gets users email and send reset code, allows for entering of the code 

            resetPassword.html                  # Allows user to enter new password

            select_utensils.html                # 2 stage form for users to select tools

            settings.html                       # All the user profile options

            shoppinglist.html                   # Shopping List UI (add/edit/remove/clear items)
        
        .env                                    # For storing environment variables.

        admin_recipe.py                         # Handles operations performed on the recipe database table when the admin recipe_view page is in use.

        alchemy_db.py                           # Loads sql alchemy with flask and handles safe execution of commands with error handling.

        app.py                                  # Main Flask app entry point. Docstrings, aided by comments explain the purpose of each function.

        database.py                             # Connects to the database using the envrionment variables set and acts as a single point to connect to the database (
                                                  for all sql commands using mariadb connector). Auto-reconnects on connection loss and handles rollbacks safely. on execute failure. 
                                                  Handles closing connection when server stops so connections don't build up on the database.
                                    
        Dockerfile                              # Docker file which includes specifications required for deployment to OpenShift.
                                                  
        email_verification.py                   # Manages user email verification through verification.
                                                  codes, sending emails, and confirming user identity.
                                                  Made through Flask's Blueprint and Flask Mail, and render_template.

        flask_forms.py                          # Handles all the flask_wtf forms used in the web app

        FoodLink.pt                             # Custom trained YOLOv8n object detection model.

        input_handling.py                       # Contains a function for validating date format as well as functions that sanitise inputs to prevent malicious 
                                                  SQl injection attacks. Both of these functions use the re module to achieve their goals.

        inventory.py                            # Handles basic CRUD sql commands for a users inventory, html form processing for adding an item to inventory,
                                                  formatting of expiry date for the front end, and more advanced sql commands: 
                                                  strict_search (used in recipe proccesing):         finds an item which is the best match for an ingredient
                                                  correct_personal_item (used in resolving reports): replaces a users personal item (with quantity checks) if their 
                                                                                                     report gets approved.
                                                  
        item.py                                 # Handles sql commands for item table, image storing functionality, and form processing.

        models.py                               # Class database models for the database tables accessed with SQLAlchemy

        notification.py                         # Handles sql commands for notification table, temp/humidity notification cooldown, and email notifications.

        recipe.py                               # Handles recipe sql commands (CRUD), and html form processing for adding and editing a recipe.

        recipe_processing.py                    # Creates a "smart recipe object" which matches a recipe against a users tools and inventory, calculates missing  
                                                  tools, finds missing or insufficient quantity ingredients, and sorts recipes by which uses most soon to expire items 
                                                  (with weighting applied).

        report.py                               # Handles SQL operations for item errors: adding user report of an item, admin get all, find duplicate and remove report
                                                  (after resolving), admins can assign a report to themselves (with override checks)

        requirements.txt                        # Python dependencies

        scanner.py                              # Processes users camera feed as a video and scans each frame using a barcode reader or AI object recogniser based on the
                                                  mode.

        settings.py                             # Handles user preferences through multiple view classes.
                                                  that control account details and notification preferences. Made through Flask's Blueprint, MethodView,
                                                  Flask Login, and werkzeug.security for password hashing.

        shopping.py                             # Handle sql commands for adding, updating removing and clearing items. Splits the list into 3 sections: Sugested Items, 
                                                  Shopping List and Bought Items.

        success.py                              # Publishes a message with the value 'Added' to ThingsBoard over secure MQTT using the tb_mqtt_client library. 
        
        thingsboard.py                          # Connect to Thingsboard using JWT tokens and fetching temperature/humidity data from telemtry.
        
        tool.py                                 # Handles tool SQL commands (CRUD)

    README.md                                   # Project README file (this file)
```

## References

Ultralytics Library for YOLO object recognition: https://github.com/ultralytics/ultralytics/tree/main/docs

Roboflow Universe for data sets: https://universe.roboflow.com/

Arduino script, feedback.py and thingsboard.py adapted sections of code from the IoT Lab Book: https://gitlab.com/IOTGarage/iot-lab-book