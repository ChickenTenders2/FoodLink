from database import connection

def get_items(user_id):
    cursor = None
    try:
        cursor = connection.cursor()
        query = """
            SELECT inv.id, i.id, i.name, i.brand, quantity, i.unit, expiry_date, i.default_quantity
            FROM FoodLink.inventory inv
            JOIN FoodLink.item i ON (inv.item_id = i.id)
            WHERE inv.user_id = %s;
        """
        cursor.execute(query, (user_id,))
        items = cursor.fetchall()
        # formats expiry date to string for front end
        items = [list(i) for i in items]
        for item in items:
            item[6] = item[6].strftime('%Y-%m-%d')
        return {"success": True, "items": items}
    except Exception as e:
        print(f"[get_items error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def search_items(user_id, search_term):
    cursor = None
    try:
        cursor = connection.cursor()
        # search query uses full text for relevance based searching of items
        query = """
            SELECT inv.id, i.id, i.name, i.brand, quantity, i.unit, expiry_date, i.default_quantity
            FROM FoodLink.inventory inv
            JOIN FoodLink.item i ON inv.item_id = i.id
            WHERE (inv.user_id = %s AND MATCH(i.name) AGAINST (%s IN NATURAL LANGUAGE MODE));
        """
        cursor.execute(query, (user_id, search_term))
        items = cursor.fetchall()
        items = [list(i) for i in items]
        for item in items:
            item[6] = item[6].strftime('%Y-%m-%d')
        return {"success": True, "items": items}
    except Exception as e:
        print(f"[search_items error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def add_item(user_id, item_id, quantity, expiry_date):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "INSERT INTO inventory (user_id, item_id, quantity, expiry_date) VALUES (%s, %s, %s, %s);"
        cursor.execute(query, (user_id, item_id, quantity, expiry_date))
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[add_item error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def process_add_form(user_id, item_id, form):
    quantity = form["quantity"]
    expiry = form["expiry_date"]
    if not quantity or not expiry:
        return {"success": False, "error": "Quantity or expiry was empty."}
    return add_item(user_id, item_id, quantity, expiry)

def remove_item(inventory_id):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "DELETE FROM inventory WHERE id = %s;"
        cursor.execute(query, (inventory_id,))
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[remove_item error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def update_quantities(items_used):
    cursor = None
    try:
        cursor = connection.cursor()
        for inventory_id, quantity in items_used:
            # Delete item if quantity is zero or less
            if quantity <= 0:
                cursor.execute("DELETE FROM inventory WHERE id = %s;", (inventory_id,))
            # Otherwise, update the quantity
            else:
                cursor.execute("UPDATE inventory SET quantity = %s WHERE id = %s;", (quantity, inventory_id))
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[update_quantities error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def update_item(inventory_id, quantity, expiry_date):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "UPDATE inventory SET quantity = %s, expiry_date = %s WHERE id = %s;"
        cursor.execute(query, (quantity, expiry_date, inventory_id))
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[update_item error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

# Replaces the users peronsal item with the item they reported once its been corrected/added to the table
# also makes sure the quantity set by the user do not exceed the corrected item max quantity
def correct_personal_item(personal_item_id, item_id, default_quantity):
    cursor = None
    try:
        cursor = connection.cursor()
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
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[correct_personal_item error] {e}")
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
