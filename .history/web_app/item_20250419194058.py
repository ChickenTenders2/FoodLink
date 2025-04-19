from database import database
from os.path import isfile as file_exists
from os import remove as remove_file
from shutil import copyfile as copy_file
import re

class item_table(database):
    def __init__(self):
        super().__init__()

    def get_all(self):
        cursor = self.connection.cursor()
        query = "SELECT * FROM FoodLink.item;"
        cursor.execute(query)
        items = cursor.fetchall()
        cursor.close()
        return items
    
    def barcode_search(self, user_id, barcode_number):
        cursor = self.connection.cursor()
        # searches for an item by barcode
        query = "SELECT id, barcode, name, brand, expiry_time, default_quantity, unit FROM FoodLink.item WHERE barcode = %s AND (user_id IS NULL OR user_id = %s);"
        data = (barcode_number, user_id)
        cursor.execute(query, data)
        item = cursor.fetchone()
        cursor.close()
        return item

    def text_search(self, user_id, search_term):
        cursor = self.connection.cursor()
        # search query uses full text for relevance based searching of items
        query = "SELECT id, barcode, name, brand, expiry_time, default_quantity, unit FROM FoodLink.item WHERE MATCH(name) AGAINST (%s IN NATURAL LANGUAGE MODE) AND (user_id IS NULL OR user_id = %s);"
        data = (search_term, user_id)
        cursor.execute(query, data)
        items = cursor.fetchall()
        cursor.close()
        return items
    
    def get_item(self, item_id):
        cursor = self.connection.cursor()
        query = "SELECT id, barcode, name, brand, expiry_time, default_quantity, unit FROM FoodLink.item WHERE id = %s;"
        data = (item_id,)
        cursor.execute(query, data)
        # gets first (and only) row
        item = cursor.fetchone()
        cursor.close()
        return item
    
    def get_default_quantity(self, item_id):
        cursor = self.connection.cursor()
        query = "SELECT default_quantity FROM FoodLink.item WHERE id = %s;"
        data = (item_id,)
        cursor.execute(query, data)
        # gets first (and only) row
        quantity = cursor.fetchone()
        cursor.close()
        return quantity
    
    def add_item(self, barcode, name, brand, expiry_time, default_quantity, unit, user_id = None):
        cursor = self.connection.cursor()
        query = "INSERT INTO FoodLink.item (barcode, name, brand, expiry_time, default_quantity, unit, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s);"
        data = (barcode, name, brand, expiry_time, default_quantity, unit, user_id)
        cursor.execute(query, data)
        self.connection.commit()
        # gets id of the item inserted
        item_id = cursor.lastrowid
        cursor.close()
        return item_id
    
    def add_item_image(self, image, new_item_id, original_item_id = None):
        if image:
                # store image in server with name item id
                path = f"static/images/{new_item_id}.jpg"
                image.save(path)
        # if a cloned item uses the original item image
        elif original_item_id:
            old_path = f"static/images/{original_item_id}.jpg"
            # makes sure original item has an image
            if file_exists(old_path):
                path = f"static/images/{new_item_id}.jpg"
                # clone the image as well
                copy_file(old_path, path)

    def process_add_form(self, form, user_id = None):
        try:
            # gets item information
            barcode = form.get("barcode") or None
            name = form.get("name")
            brand = form.get("brand") or None
            default_quantity = form.get("default_quantity")
            unit = form.get("unit")

            # gets expiry time and converts to int to remove any leading zeros
            # also checks inputs are numbers
            day = int(form.get("expiry_day"))
            month = int(form.get("expiry_month"))
            year = int(form.get("expiry_year"))

            # makes sure expire date is not 0 and that each number is within the correct range
            if (day == 0 and month == 0 and year == 0) \
                or not (0 <= day < 31 and 0 <= month < 12 and 0 <= year < 100):
                return {"success": False, "error": "Expiry time out of range."}

            # formats expiry time as string
            expiry_time = f"{day}/{month}/{year}"

            # adds item to db and gets item id
            item_id = self.add_item(barcode, name, brand, expiry_time, default_quantity, unit, user_id)

            return {"success": True, "item_id": item_id}
        except Exception as e:
            return {"success": False, "error": str(e)}
        
    def update_item(self, id, barcode, name, brand, expiry_time, default_quantity, unit, user_id = None):
        cursor = self.connection.cursor()
        query = """UPDATE FoodLink.item SET 
	                barcode = %s,
                    name = %s,
                    brand = %s,
                    expiry_time = %s,
                    default_quantity = %s,
                    unit = %s,
                    user_id = %s
                WHERE id = %s"""
        data = (barcode, name, brand, expiry_time, default_quantity, unit, user_id, id)
        cursor.execute(query, data)
        self.connection.commit()

    def process_update_form(self, id, form, user_id = None):
        try:
            # gets item information
            barcode = form.get("barcode") or None
            name = form.get("name")
            brand = form.get("brand") or None
            default_quantity = form.get("default_quantity")
            unit = form.get("unit")

            # gets expiry time and converts to int to remove any leading zeros
            # also checks inputs are numbers
            day = int(form.get("expiry_day"))
            month = int(form.get("expiry_month"))
            year = int(form.get("expiry_year"))

            # makes sure expire date is not 0 and that each number is within the correct range
            if (day == 0 and month == 0 and year == 0) \
                or not (0 <= day < 31 and 0 <= month < 12 and 0 <= year < 100):
                return {"success": False, "error": "Expiry time out of range."}

            # formats expiry time as string
            expiry_time = f"{day}/{month}/{year}"

            # updates item with id
            self.update_item(id, barcode, name, brand, expiry_time, default_quantity, unit, user_id)

            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def remove_item(self, id):
        self.remove_item_image(id)
        self.remove_item_sql(id)

    def remove_item_sql(self, id):
        cursor = self.connection.cursor()
        query = "DELETE FROM item WHERE id = %s;"
        # one item tuple
        data = (id,)
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    def remove_item_image(self, id):
        path = f"static/images/{id}.jpg"
        if file_exists(path):
            remove_file(path)


