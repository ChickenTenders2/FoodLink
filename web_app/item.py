from database import get_cursor, commit, safe_rollback
import logging
from os.path import isfile as file_exists
from os import remove as remove_file
from shutil import copyfile as copy_file
from math import ceil


##### ADMIN ONLY FUNCTIONS

def get_page(page):
    """Fetches a paginated list of global (admin) items.

    Args:
        page (int): Page number starting from 0.

    Returns:
        dict: Success status and list of items or error message.
    """
    cursor = None
    limit = 30
    try:
        offset = int(page) * limit
        cursor = get_cursor()
        query = """SELECT id, barcode, name, brand, expiry_time, default_quantity, unit 
                    FROM FoodLink.item 
                    WHERE user_id IS null
                    LIMIT %s OFFSET %s;"""
        cursor.execute(query, (limit, offset))
        items = cursor.fetchall()
        return {"success": True, "items": items}
    except Exception as e:
        logging.error(f"[item.get_page error] {e}")
        # detailed error report for admins
        return {"success": False, "error": f"[item.get_page error] {e}"}
    finally:
        if cursor:
            cursor.close()

def get_max_page():
    """Returns the maximum page number for global items based on a page size of 30.

    Returns:
        dict: Success status and max page number or error message.
    """
    cursor = None
    try:
        cursor = get_cursor()
        query = """SELECT COUNT(*) FROM FoodLink.item WHERE user_id IS null;"""
        cursor.execute(query)
        count_tuple = cursor.fetchone()
        count = count_tuple[0]
        max_pages = ceil(count / 30) - 1
        return {"success": True, "max": max_pages}
    except Exception as e:
        logging.error(f"[item.get_max_page error] {e}")
        # detailed error report for admins
        return {"success": False, "error": f"[item.get_max_page error] {e}"}
    finally:
        if cursor:
            cursor.close()

def get_item(item_id):
    """Fetches a specific item by ID.

    Args:
        item_id (int): The item ID to retrieve.

    Returns:
        dict: Success status and item details or error message.
    """
    cursor = None
    try:
        cursor = get_cursor()
        query = "SELECT id, barcode, name, brand, expiry_time, default_quantity, unit FROM FoodLink.item WHERE id = %s;"
        cursor.execute(query, (item_id,))
        item = cursor.fetchone()
        return {"success": True, "item": item}
    except Exception as e:
        logging.error(f"[item.get_item error] {e}")
        #detailed for admin
        return {"success": False, "error": f"[item.get_item error] {e}"}
    finally:
        if cursor:
            cursor.close()

def get_item_from_name(name):
    """Performs a case-insensitive search for items matching a given name.

    Args:
        name (str): The item name to search.

    Returns:
        dict: Success status and matching items or error message.
    """
    cursor = None
    try:
        cursor = get_cursor()
        query = "SELECT id, barcode, name, brand, expiry_time, default_quantity, unit FROM FoodLink.item WHERE name LIKE UPPER(%s);"
        cursor.execute(query, (name,))
        items = cursor.fetchall()
        return {"success": True, "items": items}
    except Exception as e:
        logging.error(f"[item.get_item_from_name error] {e}")
        # deailed error report for admins
        return {"success": False, "error": f"[item.get_item_from_name error] {e}"}
    finally:
        if cursor:
            cursor.close()

def get_default_quantity(item_id):
    """Fetches the default quantity value for an item.

    Args:
        item_id (int): ID of the item.

    Returns:
        dict: Success status and quantity or error message.
    """
    cursor = None
    try:
        cursor = get_cursor()
        cursor.execute("SELECT default_quantity FROM FoodLink.item WHERE id = %s;", (item_id,))
        quantity_tuple = cursor.fetchone()
        # unpack tuple
        quantity = quantity_tuple[0]
        return {"success": True, "quantity": quantity}
    except Exception as e:
        logging.error(f"[get_default_quantity error] {e}")
        # more detailed report for admin only function
        return {"success": False, "error": f"[get_default_quantity error] {e}"}
    finally:
        if cursor:
            cursor.close()


##### USER + ADMIN FUNCTIONS
            
def get_personal(user_id):
    """
    Retrieves all items added by a specific user.

    Args:
        user_id (int): ID of the user.

    Returns:
        dict: Contains success status and either a list of items or an error message.
    """
    cursor = None
    try:
        cursor = get_cursor()
        # search query uses full text for relevance based searching of items
        query = "SELECT id, barcode, name, brand, expiry_time, default_quantity, unit, TRUE AS is_personal FROM FoodLink.item WHERE user_id = %s;"
        data = (user_id,)
        cursor.execute(query, data)
        items = cursor.fetchall()
        return {"success": True, "items": items}
    except Exception as e:
        logging.error(f"[item.get_personal error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def barcode_search(user_id, barcode_number):
    """
    Searches for an item by barcode, prioritizing the user's personal item if it exists.

    Args:
        user_id (int): ID of the user.
        barcode_number (str): Barcode number to search for.

    Returns:
        dict: Contains success status and either the found item or an error message.
    """
    cursor = None
    try:
        cursor = get_cursor()
        # searches for an item by barcode
        query = """SELECT id, barcode, name, brand, expiry_time, default_quantity, unit, 
                    CASE WHEN user_id = %s THEN TRUE ELSE FALSE END AS is_personal 
                    FROM FoodLink.item 
                    WHERE barcode = %s 
                    AND (user_id IS NULL OR user_id = %s)
                    ORDER BY (user_id = %s) DESC;"""
        data = (user_id, barcode_number, user_id, user_id)
        cursor.execute(query, data)
        item = cursor.fetchone()
        return {"success": True, "item": item}
    except Exception as e:
        logging.error(f"[item.barcode_search error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def text_search(user_id, search_term):
    """
    Performs a full-text search for items based on the name, returning multiple matches.

    Args:
        user_id (int): ID of the user.
        search_term (str): Text to search for in item names.

    Returns:
        dict: Contains success status and either a list of items or an error message.
    """
    cursor = None
    try:
        cursor = get_cursor()
        # search query uses full text for relevance based searching of items
        query = """SELECT id, barcode, name, brand, expiry_time, default_quantity, unit, 
                    CASE WHEN user_id = %s THEN TRUE ELSE FALSE END AS is_personal 
                    FROM FoodLink.item 
                    WHERE MATCH(name) AGAINST (%s IN NATURAL LANGUAGE MODE) 
                    AND (user_id IS NULL OR user_id = %s)
                    ORDER BY (user_id = %s) DESC;"""
        data = (user_id, search_term, user_id, user_id)
        cursor.execute(query, data)
        items = cursor.fetchall()
        return {"success": True, "items": items}
    except Exception as e:
        logging.error(f"[item.text_search error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def text_single_search(user_id, search_term):
    """
    Performs a full-text search for a single item based on the name.

    Args:
        user_id (int): ID of the user.
        search_term (str): Text to search for in item names.

    Returns:
        dict: Contains success status and either a single item or an error message.
    """
    cursor = None
    try:
        cursor = get_cursor()
        # search query uses full text for relevance based searching of items
        query = """SELECT id, barcode, name, brand, expiry_time, default_quantity, unit, 
                    CASE WHEN user_id = %s THEN TRUE ELSE FALSE END AS is_personal 
                    FROM FoodLink.item 
                    WHERE MATCH(name) AGAINST (%s IN NATURAL LANGUAGE MODE) 
                    AND (user_id IS NULL OR user_id = %s) 
                    ORDER BY (user_id = %s) DESC;"""
        data = (user_id, search_term, user_id, user_id)
        cursor.execute(query, data)
        item = cursor.fetchone()
        return {"success": True, "item": item}
    except Exception as e:
        logging.error(f"[item.text_single_search error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def add_item(barcode, name, brand, expiry_time, default_quantity, unit, user_id=None):
    """
    Adds a new item to the database.

    Args:
        barcode (str): Item's barcode.
        name (str): Item name.
        brand (str): Brand name.
        expiry_time (str): Expiry date in "day/month/year" format.
        default_quantity (str): Default quantity of the item.
        unit (str): Unit of measurement.
        user_id (int, optional): ID of the user adding the item.

    Returns:
        dict: Contains success status and the new item's ID or an error message.
    """
    cursor = None
    try:
        cursor = get_cursor()
        query = "INSERT INTO FoodLink.item (barcode, name, brand, expiry_time, default_quantity, unit, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s);"
        cursor.execute(query, (barcode, name, brand, expiry_time, default_quantity, unit, user_id))
        commit()
        # gets id of the item inserted
        item_id = cursor.lastrowid
        return {"success": True, "item_id": item_id}
    except Exception as e:
        safe_rollback()
        logging.error(f"[add_item error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

# no returns, as images arent important enough to return a whole request as failed
def add_item_image(image, new_item_id, original_item_id=None):
    """
    Saves an uploaded image for an item or clones an image from an existing item.

    Args:
        image (FileStorage): Uploaded image file.
        new_item_id (int): ID of the new item.
        original_item_id (int, optional): ID of the original item to copy image from.
    """
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
        logging.error(f"[add_item_image error] {e}")

def process_add_form(form, user_id=None):
    """
    Processes a submitted form to add a new item.

    Args:
        form (ImmutableMultiDict): Form containing item details.
        user_id (int, optional): ID of the user submitting the form.

    Returns:
        dict: Contains success status or an error message.
    """
    # gets item information
    barcode = form.get("barcode") or None
    name = form.get("name")
    brand = form.get("brand") or None
    default_quantity = form.get("default_quantity")
    unit = form.get("unit")

    if not (name and default_quantity and unit):
        return {"success": False, "error": "Required value(s) missing."}

    day_str = form.get("expiry_day")
    month_str = form.get("expiry_month")
    year_str = form.get("expiry_year")

    if not (day_str and month_str and year_str):
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
    """
    Updates an existing item in the database.

    Args:
        id (int): Item ID.
        barcode (str): Updated barcode.
        name (str): Updated item name.
        brand (str): Updated brand.
        expiry_time (str): Updated expiry date.
        default_quantity (str): Updated quantity.
        unit (str): Updated unit.
        user_id (int, optional): ID of the user performing the update.

    Returns:
        dict: Contains success status or an error message.
    """
    ## if user submitted update, make sure theyre modifying their own item
    if user_id:
        result = owner_check(id, user_id)
        if not result.get("success"):
            return result
    cursor = None
    try:
        cursor = get_cursor()
        query = f"""UPDATE FoodLink.item SET 
                    barcode = %s,
                    name = %s,
                    brand = %s,
                    expiry_time = %s,
                    default_quantity = %s,
                    unit = %s,
                    user_id = %s 
                WHERE id = %s;""" 
        data = (barcode, name, brand, expiry_time, default_quantity, unit, user_id, id)
        cursor.execute(query, data)
        commit()
        return {"success": True}
    except Exception as e:
        safe_rollback()
        logging.error(f"[update_item error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def process_update_form(id, form, user_id=None):
    """
    Processes a submitted form to update an existing item.

    Args:
        id (int): ID of the item to update.
        form (ImmutableMultiDict): Form containing updated item details.
        user_id (int, optional): ID of the user submitting the form.

    Returns:
        dict: Contains success status or an error message.
    """
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

    if not (day_str and month_str and year_str):
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

    # updates item with id
    return update_item(id, barcode, name, brand, expiry_time, default_quantity, unit, user_id)

def remove_item(id, user_id = None):
    """
    Deletes an item, ensuring only the item's owner can delete it if user_id is provided.

    Args:
        id (int): ID of the item to delete.
        user_id (int, optional): ID of the user attempting deletion.

    Returns:
        dict: Contains success status or an error message.
    """
    ## if user submitted, make sure theyre deleting their own item
    if user_id:
        result = owner_check(id, user_id)
        if not result.get("success"):
            return result
    # error removing item image is minor so doesnt effect result
    remove_item_image(id)
    user_item = True if user_id else False
    return remove_item_sql(id, user_item)

def remove_item_sql(id, user_item):
    """
    Deletes an item and related records from the database.

    Args:
        id (int): Item ID.
        user_item (bool): Indicates whether the item is user-specific.

    Returns:
        dict: Contains success status or an error message.
    """
    cursor = None
    try:
        cursor = get_cursor()
        cursor.execute("DELETE FROM item WHERE id = %s;", (id,))
        if user_item:
            # makes sure item is removed from inventories aswell
            cursor.execute("DELETE FROM inventory WHERE item_id = %s", (id,))
            # makes sure item report is removed aswell (if reported)
            cursor.execute("DELETE FROM item_error WHERE new_item_id = %s", (id,))
        commit()
        return {"success": True}
    except Exception as e:
        safe_rollback()
        logging.error(f"[remove_item_sql error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def remove_item_image(id):
    """
    Deletes the image file associated with an item.

    Args:
        id (int): Item ID whose image should be deleted.
    """
    try:
        path = f"static/images/{id}.jpg"
        if file_exists(path):
            remove_file(path)
    except Exception as e:
        logging.error(f"[remove_item_image error] {e}")


# checks if user is modifying their own item
def owner_check(id, user_id):
    """
    Verifies that a user is the owner of a given item.

    Args:
        id (int): Item ID.
        user_id (int): User ID to check ownership.

    Returns:
        dict: Contains success status or an error message.
    """
    cursor = None
    try:
        cursor = get_cursor()
        cursor.execute("SELECT user_id FROM FoodLink.item WHERE id = %s;", (id,))
        result = cursor.fetchone()
        if not result or result[0] != user_id:
            return {"success": False, "error": "Permission denied."}
        return {"success": True}
    except Exception as e:
        logging.error(f"[item.owner_check error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()
