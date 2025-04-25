from database import connection
from os.path import isfile as file_exists
from os import remove as remove_file
from shutil import copyfile as copy_file


##### ADMIN ONLY FUNCTIONS

def get_all():
    cursor = None
    try:
        cursor = connection.cursor()
        query = "SELECT id, barcode, name, brand, expiry_time, default_quantity, unit FROM FoodLink.item WHERE user_id IS null;"
        cursor.execute(query)
        items = cursor.fetchall()
        return {"success": True, "items": items}
    except Exception as e:
        print(f"[item.get_all error] {e}")
        # detailed error report for admins
        return {"success": False, "error": f"[item.get_all error] {e}"}
    finally:
        if cursor:
            cursor.close()


def get_item(item_id):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "SELECT id, barcode, name, brand, expiry_time, default_quantity, unit FROM FoodLink.item WHERE id = %s;"
        cursor.execute(query, (item_id,))
        item = cursor.fetchone()
        return {"success": True, "item": item}
    except Exception as e:
        print(f"[item.get_item error] {e}")
        #detailed for admin
        return {"success": False, "error": f"[item.get_item error] {e}"}
    finally:
        if cursor:
            cursor.close()

def get_item_from_name(name):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "SELECT id, barcode, name, brand, expiry_time, default_quantity, unit FROM FoodLink.item WHERE name LIKE UPPER(%s);"
        cursor.execute(query, (name,))
        items = cursor.fetchall()
        return {"success": True, "items": items}
    except Exception as e:
        print(f"[item.get_item_from_name error] {e}")
        # deailed error report for admins
        return {"success": False, "error": f"[item.get_item_from_name error] {e}"}
    finally:
        if cursor:
            cursor.close()

def get_default_quantity(item_id):
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT default_quantity FROM FoodLink.item WHERE id = %s;", (item_id,))
        quantity_tuple = cursor.fetchone()
        # unpack tuple
        quantity = quantity_tuple[0]
        return {"success": True, "quantity": quantity}
    except Exception as e:
        print(f"[get_default_quantity error] {e}")
        # more detailed report for admin only function
        return {"success": False, "error": f"[get_default_quantity error] {e}"}
    finally:
        if cursor:
            cursor.close()


##### USER + ADMIN FUNCTIONS

def barcode_search(user_id, barcode_number):
    cursor = None
    try:
        cursor = connection.cursor()
        # searches for an item by barcode
        query = "SELECT id, barcode, name, brand, expiry_time, default_quantity, unit FROM FoodLink.item WHERE barcode = %s AND (user_id IS NULL OR user_id = %s);"
        data = (barcode_number, user_id)
        cursor.execute(query, data)
        item = cursor.fetchone()
        return {"success": True, "item": item}
    except Exception as e:
        print(f"[item.barcode_search error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def text_search(user_id, search_term):
    cursor = None
    try:
        cursor = connection.cursor()
        # search query uses full text for relevance based searching of items
        query = "SELECT id, barcode, name, brand, expiry_time, default_quantity, unit FROM FoodLink.item WHERE MATCH(name) AGAINST (%s IN NATURAL LANGUAGE MODE) AND (user_id IS NULL OR user_id = %s);"
        data = (search_term, user_id)
        cursor.execute(query, data)
        items = cursor.fetchall()
        return {"success": True, "items": items}
    except Exception as e:
        print(f"[item.text_search error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def text_single_search(user_id, search_term):
    cursor = None
    try:
        cursor = connection.cursor()
        # search query uses full text for relevance based searching of items
        query = "SELECT id, barcode, name, brand, expiry_time, default_quantity, unit FROM FoodLink.item WHERE MATCH(name) AGAINST (%s IN NATURAL LANGUAGE MODE) AND (user_id IS NULL OR user_id = %s);"
        data = (search_term, user_id)
        cursor.execute(query, data)
        item = cursor.fetchone()
        return {"success": True, "item": item}
    except Exception as e:
        print(f"[item.text_single_search error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def add_item(barcode, name, brand, expiry_time, default_quantity, unit, user_id=None):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "INSERT INTO FoodLink.item (barcode, name, brand, expiry_time, default_quantity, unit, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s);"
        cursor.execute(query, (barcode, name, brand, expiry_time, default_quantity, unit, user_id))
        connection.commit()
        # gets id of the item inserted
        item_id = cursor.lastrowid
        return {"success": True, "item_id": item_id}
    except Exception as e:
        print(f"[add_item error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

# no returns, as images arent important enough to return a whole request as failed
def add_item_image(image, new_item_id, original_item_id=None):
    try:
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
    except Exception as e:
        print(f"[add_item_image error] {e}")

def process_add_form(form, user_id=None):
    # gets item information
    barcode = form.get("barcode") or None
    name = form.get("name")
    brand = form.get("brand") or None
    default_quantity = form.get("default_quantity")
    unit = form.get("unit")

    if not name or not default_quantity or not unit:
        return {"success": False, "error": "Required value(s) missing."}

    day_str = form.get("expiry_day")
    month_str = form.get("expiry_month")
    year_str = form.get("expiry_year")

    if not day_str or not month_str or not year_str:
        return {"success": False, "error": "Expiry time value(s) missing."}
    
    if not (day_str.isdigit() and month_str.isdigit() and year_str.isdigit()):
        return {"success": False, "error": "Expiry time value(s) must be numbers."}

    day = int(day_str)
    month = int(month_str)
    year = int(year_str)

    # makes sure expire date is not 0 and that each number is within the correct range
    if (day == 0 and month == 0 and year == 0) \
        or not (0 <= day < 31 and 0 <= month < 12 and 0 <= year < 100):
        return {"success": False, "error": "Expiry time out of range."}

    # formats expiry time as string
    expiry_time = f"{day}/{month}/{year}"

    # adds item to db and gets item id
    return add_item(barcode, name, brand, expiry_time, default_quantity, unit, user_id)

def update_item(id, barcode, name, brand, expiry_time, default_quantity, unit, user_id=None):
    cursor = None
    try:
        cursor = connection.cursor()
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
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[update_item error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def process_update_form(id, form, user_id=None):
    # gets item information
    barcode = form.get("barcode") or None
    name = form.get("name")
    brand = form.get("brand") or None
    default_quantity = form.get("default_quantity")
    unit = form.get("unit")

    if not name or not default_quantity or not unit:
        return {"success": False, "error": "Required value(s) missing."}
    
    # gets expiry time and converts to int to remove any leading zeros
    # also checks inputs are numbers
    day = int(form.get("expiry_day"))
    month = int(form.get("expiry_month"))
    year = int(form.get("expiry_year"))

    if not day or not month or not year:
        return {"success": False, "error": "Expiry time value(s) missing."}

    # makes sure expire date is not 0 and that each number is within the correct range
    if (day == 0 and month == 0 and year == 0) \
        or not (0 <= day < 31 and 0 <= month < 12 and 0 <= year < 100):
        return {"success": False, "error": "Expiry time out of range."}

    # formats expiry time as string
    expiry_time = f"{day}/{month}/{year}"

    # updates item with id
    return update_item(id, barcode, name, brand, expiry_time, default_quantity, unit, user_id)

def remove_item(id):
    # error removing item image is minor so doesnt effect result
    remove_item_image(id)
    return remove_item_sql(id)

def remove_item_sql(id):
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM item WHERE id = %s;", (id,))
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[remove_item_sql error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def remove_item_image(id):
    try:
        path = f"static/images/{id}.jpg"
        if file_exists(path):
            remove_file(path)
    except Exception as e:
        print(f"[remove_item_image error] {e}")

