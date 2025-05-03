import sys
import os

# Add the root directory (parent of itemDB.py) to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ROOT_DIR)

from web_app.database import get_cursor, commit, safe_rollback

import logging

items = {
    'Bacon': {'brand': 'Tesco', 'barcode': 5052004794732, 'expiry_time': '30/0/0', 'default_quantity': 300, 'unit': 'grams'},
    'Baguette': {'brand': 'Generic', 'barcode': None, 'expiry_time': '5/0/0', 'default_quantity': 1, 'unit': 'pieces'},
    'Baking Powder': {'brand': 'Generic', 'barcode': None, 'expiry_time': '0/0/1', 'default_quantity': 100, 'unit': 'grams'},
    'Bean Sprouts': {'brand': 'Generic', 'barcode': None, 'expiry_time': '3/0/0', 'default_quantity': 100, 'unit': 'grams'},
    'Black Pepper': {'brand': 'Generic', 'barcode': None, 'expiry_time': '0/0/2', 'default_quantity': 100, 'unit': 'grams'},
    'Brown Sugar': {'brand': 'Tesco', 'barcode': 5000119113252, 'expiry_time': '0/0/2', 'default_quantity': 500, 'unit': 'grams'},
    'Celery': {'brand': 'Generic', 'barcode': None, 'expiry_time': '14/0/0', 'default_quantity': 1, 'unit': 'celery sticks'},
    'Cumin Powder': {'brand': 'Generic', 'barcode': None, 'expiry_time': '0/0/2', 'default_quantity': 100, 'unit': 'grams'},
    'Dumpling Wrappers': {'brand': 'Generic', 'barcode': None, 'expiry_time': '14/0/0', 'default_quantity': 50, 'unit': 'wrapper'},
    'Ginger': {'brand': 'Generic', 'barcode': None, 'expiry_time': '30/0/0', 'default_quantity': 1, 'unit': 'ginger'},
    'Green Onions': {'brand': 'Generic', 'barcode': None, 'expiry_time': '7/0/0', 'default_quantity': 1, 'unit': 'green onions'},
    'Ground Beef': {'brand': 'Generic', 'barcode': None, 'expiry_time': '7/0/0', 'default_quantity': 500, 'unit': 'grams'},
    'Lasagna Sheets': {'brand': 'Baresa', 'barcode': 4056489633341, 'expiry_time': '0/0/2', 'default_quantity': 500, 'unit': 'grams'},
    'Lemon Juice': {'brand': 'Generic', 'barcode': None, 'expiry_time': '30/0/0', 'default_quantity': 250, 'unit': 'ml'},
    'Mirin': {'brand': 'Blue Dragon', 'barcode': 5010338016302 , 'expiry_time': '0/6/0', 'default_quantity': 250, 'unit': 'ml'},
    'Mozzarella Cheese': {'brand': 'Generic', 'barcode': None, 'expiry_time': '0/3/0', 'default_quantity': 200, 'unit': 'grams'},
    'Paprika': {'brand': 'Generic', 'barcode': None, 'expiry_time': '0/0/2', 'default_quantity': 100, 'unit': 'grams'},
    'Parsley': {'brand': 'Generic', 'barcode': None, 'expiry_time': '7/0/0', 'default_quantity': 100, 'unit': 'grams'},
    'Peanuts': {'brand': 'Generic', 'barcode': None, 'expiry_time': '0/6/0', 'default_quantity': 200, 'unit': 'grams'},
    'Red Lentils': {'brand': 'East End', 'barcode': 5018605811308, 'expiry_time': '0/0/2', 'default_quantity': 500, 'unit': 'grams'},
    'Salt': {'brand': 'Generic', 'barcode': None, 'expiry_time': '0/0/2', 'default_quantity': 500, 'unit': 'grams'},
    'Spinach': {'brand': 'Generic', 'barcode': None, 'expiry_time': '7/0/0', 'default_quantity': 100, 'unit': 'grams'},
    'Sugar': {'brand': 'Generic', 'barcode': None, 'expiry_time': '0/0/2', 'default_quantity': 500, 'unit': 'grams'},
    'Taco Seasoning': {'brand': 'Old El Paso', 'barcode': 8410076491893, 'expiry_time': '0/0/2', 'default_quantity': 100, 'unit': 'grams'},
    'Taco Shells': {'brand': 'Old El Paso', 'barcode': 8410076480637, 'expiry_time': '0/0/1', 'default_quantity': 12, 'unit': 'pieces'},
    'Tahini': {'brand': 'Belazu', 'barcode': 5030343833824, 'expiry_time': '0/6/0', 'default_quantity': 1000, 'unit': 'ml'},
    'Tofu': {'brand': 'Generic', 'barcode': None, 'expiry_time': '7/0/0', 'default_quantity': 250, 'unit': 'grams'},
    'Tomato Paste': {'brand': 'Generic', 'barcode': None, 'expiry_time': '0/6/0', 'default_quantity': 250, 'unit': 'grams'},
    'Tomato Sauce': {'brand': 'Generic', 'barcode': None, 'expiry_time': '0/6/0', 'default_quantity': 250, 'unit': 'ml'},
    'Wakame Seaweed': {'brand': 'Generic', 'barcode': None, 'expiry_time': '0/6/0', 'default_quantity': 50, 'unit': 'grams'},
    'Yogurt': {'brand': 'Generic', 'barcode': None, 'expiry_time': '0/1/0', 'default_quantity': 250, 'unit': 'ml'}
}


cursor = get_cursor()
try:
    for name, details in items.items():
        cursor.execute(
            """
            INSERT INTO item (barcode, name, brand, expiry_time, default_quantity, unit, user_id)
            VALUES (?, ?, ?, ?, ?, ?, NULL)
            """,
            (
                details["barcode"],
                name,
                details["brand"],
                details["expiry_time"],
                details["default_quantity"],
                details["unit"]
            )
        )
    commit()
    logging.info(f"[INFO] Inserted {len(items)} new items successfully.")
except Exception as e:
    logging.error(f"[ERROR] Failed to insert items: {e}")
    safe_rollback()
    raise