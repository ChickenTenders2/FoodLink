from database import get_cursor, commit, safe_rollback
import logging


# Retrieve all shopping list items for a given user
def get_items(user_id):
    """
    Retrieve all shopping list items for a specific user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        dict: Contains a list of items if successful, otherwise an error message.
    """
    cursor = None
    try:
        cursor = get_cursor()
        query = "SELECT id, item_name, quantity, bought FROM FoodLink.shopping_list WHERE user_id = %s;"
        data = (user_id,)
        cursor.execute(query, data)
        items = cursor.fetchall()
        return {"success": True, "items": items}
    except Exception as e:
        logging.error(f"[get_items error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

# Add a single item to the shopping list
def add_item(user_id, item_name, quantity):
    """
    Add a single item to the shopping list.

    Args:
        user_id (int): The ID of the user.
        item_name (str): Name of the item to add.
        quantity (int): Quantity of the item.

    Returns:
        dict: Success status, action performed, and item name.
    """
    cursor = None
    try:
        cursor = get_cursor()
        cursor.execute("INSERT INTO shopping_list (user_id, item_name, quantity) VALUES (%s, %s, %s)", (user_id, item_name, quantity))
        commit()
        return {"success": True, "action": "add", "item": item_name}
    except Exception as e:
        safe_rollback()
        logging.error(f"[add_item error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

# Add multiple items to the shopping list at once
def add_items(user_id, items):
    """
    Add multiple items to the shopping list.

    Args:
        user_id (int): The ID of the user.
        items (list of tuple): A list of (item_name, quantity) tuples.

    Returns:
        dict: Success status or error message.
    """
    cursor = None
    try:
        cursor = get_cursor()
        data = [(user_id, item[0], item[1]) for item in items]
        query = "INSERT INTO shopping_list (user_id, item_name, quantity) VALUES (%s, %s, %s)"
        cursor.executemany(query, data)
        commit()
        return {"success": True}
    except Exception as e:
        safe_rollback()
        logging.error(f"[add_items error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

# Update the name and/or quantity of an existing item in the shopping list
def update_item(user_id, item_id, item_name, quantity):
    """
    Update the name or quantity of an existing item in the shopping list.

    Args:
        user_id (int): The ID of the user.
        item_id (int): The ID of the item to update.
        item_name (str): The new item name.
        quantity (int): The new quantity.

    Returns:
        dict: Success status, action performed, and updated item name.
    """
    cursor = None
    try:
        cursor = get_cursor()
        query = "UPDATE shopping_list SET item_name = %s, quantity = %s WHERE id = %s AND user_id = %s"
        data = (item_name, quantity, item_id, user_id)
        cursor.execute(query, data)
        commit()
        return {"success": True, "action": "update", "item": item_name}
    except Exception as e:
        safe_rollback()
        logging.error(f"[update_item error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

# Mark an item as bought or unbought
def item_bought(user_id, item_id, bought):
    """
    Mark a shopping list item as bought or unbought.

    Args:
        user_id (int): The ID of the user.
        item_id (int): The ID of the item.
        bought (bool or int): 1 if bought, 0 if not.

    Returns:
        dict: Success status and action.
    """
    cursor = None
    try:
        cursor = get_cursor()
        query = "UPDATE shopping_list SET bought = %s WHERE id = %s AND user_id = %s"
        data = (bought, item_id, user_id)
        cursor.execute(query, data)
        commit()
        return {"success": True, "action": "mark_bought"}
    except Exception as e:
        safe_rollback()
        logging.error(f"[item_bought error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

# Retrieve items from the inventory that are low in stock
def low_stock_items(user_id):
    """
    Retrieve inventory items that are low in stock for the user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        dict: Success status and a list of low-stock items.
    """
    cursor = None
    try:
        cursor = get_cursor()
        query = "SELECT i.name, i.default_quantity, inv.quantity FROM inventory inv JOIN item i ON inv.item_id = i.id WHERE inv.user_id = %s AND inv.quantity <= i.default_quantity / 10"
        data = (user_id,)
        cursor.execute(query, data)
        items = cursor.fetchall()
        return {"success": True, "items": items}
    except Exception as e:
        logging.error(f"[low_stock_items error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

# Remove a specific item from the shopping list
def remove_item(user_id, item_id):
    """
    Remove a specific item from the shopping list.

    Args:
        user_id (int): The ID of the user.
        item_id (int): The ID of the item to remove.

    Returns:
        dict: Success status and removed item ID.
    """
    cursor = None
    try:
        cursor = get_cursor()
        cursor.execute("DELETE FROM shopping_list WHERE id = %s AND user_id = %s", (item_id, user_id))
        commit()
        return {"success": True, "action": "remove", "item_id": item_id}
    except Exception as e:
        safe_rollback()
        logging.error(f"[remove_item error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

# Clear the entire shopping list for a given user
def clear_items(user_id):
    """
    Clear all items from the user's shopping list.

    Args:
        user_id (int): The ID of the user.

    Returns:
        dict: Success status and action performed.
    """
    cursor = None
    try:
        cursor = get_cursor()
        cursor.execute("DELETE FROM shopping_list WHERE user_id = %s", (user_id,))
        commit()
        return {"success": True, "action": "clear"}
    except Exception as e:
        safe_rollback()
        logging.error(f"[clear_items error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()
