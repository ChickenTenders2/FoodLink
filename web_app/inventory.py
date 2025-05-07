from database import get_cursor, commit, safe_rollback
import logging

def get_items(user_id):
    """
    Fetches all inventory items for a given user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        dict: A success flag and list of formatted items, or error message on failure.
    """
    cursor = None
    try:
        cursor = get_cursor()
        query = """
            SELECT inv.id, i.id, i.name, i.brand, quantity, i.unit, expiry_date, i.default_quantity
            FROM FoodLink.inventory inv
            JOIN FoodLink.item i ON (inv.item_id = i.id)
            WHERE inv.user_id = %s;
        """
        cursor.execute(query, (user_id,))
        items = cursor.fetchall()
        items = format_items(items)
        return {"success": True, "items": items}
    except Exception as e:
        logging.error(f"[get_items error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def search_items(user_id, search_term):
    """
    Performs a full-text search for items in the user's inventory.

    Args:
        user_id (int): The user ID.
        search_term (str): The search string for item names.

    Returns:
        dict: A success flag and list of matched items, or error message on failure.
    """
    cursor = None
    try:
        cursor = get_cursor()
        # search query uses full text for relevance based searching of items
        query = """
            SELECT inv.id, i.id, i.name, i.brand, quantity, i.unit, expiry_date, i.default_quantity
            FROM FoodLink.inventory inv
            JOIN FoodLink.item i ON inv.item_id = i.id
            WHERE (inv.user_id = %s AND MATCH(i.name) AGAINST (%s IN NATURAL LANGUAGE MODE));
        """
        cursor.execute(query, (user_id, search_term))
        items = cursor.fetchall()
        items = format_items(items)
        return {"success": True, "items": items}
    except Exception as e:
        logging.error(f"[search_items error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def add_item(user_id, item_id, quantity, expiry_date):
    """
    Adds a new item to the user's inventory.

    Args:
        user_id (int): User ID.
        item_id (int): Item ID.
        quantity (int or float): Quantity of the item.
        expiry_date (str): Expiry date in ISO format.

    Returns:
        dict: Success status or error.
    """
    cursor = None
    try:
        cursor = get_cursor()
        query = "INSERT INTO inventory (user_id, item_id, quantity, expiry_date) VALUES (%s, %s, %s, %s);"
        cursor.execute(query, (user_id, item_id, quantity, expiry_date))
        commit()
        return {"success": True}
    except Exception as e:
        safe_rollback()
        logging.error(f"[add_item error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def process_add_form(user_id, item_id, form):
    """
    Processes form data to add an item.

    Args:
        user_id (int): User ID.
        item_id (int): Item ID.
        form (dict): Dictionary containing 'quantity' and 'expiry_date'.

    Returns:
        dict: Result from add_item or error if missing fields.
    """
    quantity = form["quantity"]
    expiry = form["expiry_date"]
    if not quantity or not expiry:
        return {"success": False, "error": "Quantity or expiry was empty."}
    return add_item(user_id, item_id, quantity, expiry)

def remove_item(inventory_id, user_id):
    """Delete an item from the database with id."""
    cursor = None
    try:
        cursor = get_cursor()
        query = "DELETE FROM inventory WHERE id = %s AND user_id = %s;"
        cursor.execute(query, (inventory_id, user_id))
        commit()
        return {"success": True}
    except Exception as e:
        safe_rollback()
        logging.error(f"[remove_item error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def update_quantities(items_used, user_id):
    """
    Updates the quantity for multiple items.

    Args:
        items_used ([list]): List of lists in form (inventory_id, quantity)

    Returns:
        dict: A dictionary with success value (True,False) and possibly an error message
    """
    cursor = None
    try:
        cursor = get_cursor()
        for inventory_id, quantity in items_used:
            # Delete item if quantity is zero or less
            if quantity <= 0:
                cursor.execute("DELETE FROM inventory WHERE id = %s AND user_id = %s;", (inventory_id, user_id))
            # Otherwise, update the quantity
            else:
                cursor.execute("UPDATE inventory SET quantity = %s WHERE id = %s AND user_id = %s;", (quantity, inventory_id, user_id))
        commit()
        return {"success": True}
    except Exception as e:
        safe_rollback()
        logging.error(f"[update_quantities error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def update_item(inventory_id, quantity, expiry_date, user_id):
    """Updates the quantity and expiry date of an item with id."""
    cursor = None
    try:
        cursor = get_cursor()
        query = "UPDATE inventory SET quantity = %s, expiry_date = %s WHERE id = %s AND user_id = %s;"
        cursor.execute(query, (quantity, expiry_date, inventory_id))
        commit()
        return {"success": True}
    except Exception as e:
        safe_rollback()
        logging.error(f"[update_item error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()


def correct_personal_item(personal_item_id, item_id, default_quantity):
    """Replaces the users personal item in their inventory with the item they reported once its been corrected/added to the table publicly.
    Ensuring the quantity set by the user do not exceed the corrected item max quantity."""
    cursor = None
    try:
        cursor = get_cursor()
        # item_id = the item id of the now added item if missing, or the item id of the item that has now been corrected
        # personal_item_id = the users personal item id that they added before reporting

        # if default quantity is 1 then there is not a limit on the quantity
        if default_quantity == 1:
            query = "UPDATE FoodLink.inventory SET item_id = %s WHERE item_id = %s;"
            data = (item_id, personal_item_id)
        # otherwise the users item should not exceed the default quantity (max amount) of the item
        else:
            # sets quantity to max if it exceeds limit
            query = """
                UPDATE FoodLink.inventory SET 
                    item_id = %s,
                    quantity = CASE
                        WHEN quantity > %s THEN %s
                        ELSE quantity
                    END
                WHERE item_id = %s;
            """
            data = (item_id, default_quantity, default_quantity, personal_item_id)
        cursor.execute(query, data)
        commit()
        return {"success": True}
    except Exception as e:
        safe_rollback()
        logging.error(f"[correct_personal_item error] {e}")
        # detailed error report for admins
        return {"success": False, 
                "error": f"""[correct_personal_item error]:
                Inputs: 
                personal_item_id: {personal_item_id},
                item_id: {item_id},
                default_quantity: {default_quantity},
                Error: {e}"""
            }
    finally:
        if cursor:
            cursor.close()


def strict_search(user_id, item_name, quantity_threshold):
    """Returns the best match for an ingredient that a user has in their inventory."""
    cursor = None
    try:
        cursor = get_cursor()
        # gets each word in item name seperately
        terms = item_name.strip().split()
        # adds a + before each word to make sure that results must include ALL words in the item name
        boolean_search = " ".join(f"+{word}" for word in terms)
        # gets items which fully match the name, and are still in date
        # then sorts by items with:
        #   atleast 95% of the quantity first, so the meal is not altered to drastically
        #   then prioritising soon to expire items, which makes sure they get used first, reducing food waste
        #   then prioritising smaller quantities, to make sure an item with less quantity gets used up first
        query = """
            SELECT inv.id, i.id, i.name, i.brand, quantity, i.unit, expiry_date
            FROM FoodLink.inventory inv
            JOIN FoodLink.item i ON inv.item_id = i.id
            WHERE inv.user_id = %s 
            AND MATCH(i.name) AGAINST (%s IN BOOLEAN MODE)
            AND inv.expiry_date > CURRENT_DATE
            ORDER BY
                CASE WHEN inv.quantity >= %s THEN 1 ELSE 0 END DESC,   
                inv.expiry_date ASC,
                inv.quantity ASC;
        """
        data = (user_id, boolean_search, quantity_threshold)
        cursor.execute(query, data)
        item = cursor.fetchone()
        return {"success": True, "item": item}
    except Exception as e:
        logging.error(f"[strict_search error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()


def format_items(items):
    """Formats date in list of items for frontend."""
    return [format_item(item) for item in items]

# formats date of item to string for front end
def format_item(item):
    """Formats date in item."""
    item = list(item)
    item[6] = item[6].isoformat()
    return item

