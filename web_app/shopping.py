from database import connection

def get_items(user_id):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "SELECT id, item_name, quantity, bought FROM FoodLink.shopping_list WHERE user_id = %s;"
        data = (user_id,)
        cursor.execute(query, data)
        items = cursor.fetchall()
        return {"success": True, "data": items}
    except Exception as e:
        print(f"[get_items error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def add_item(user_id, item_name, quantity):
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO shopping_list (user_id, item_name, quantity) VALUES (%s, %s, %s)", (user_id, item_name, quantity))
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[add_item error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def add_items(user_id, items):
    cursor = None
    try:
        cursor = connection.cursor()
        data = [(user_id, item[0], item[1]) for item in items]
        query = "INSERT INTO shopping_list (user_id, item_name, quantity) VALUES (%s, %s, %s)"
        cursor.executemany(query, data)
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[add_items error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def update_item(item_id, item_name, quantity):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "UPDATE shopping_list SET item_name = %s, quantity = %s WHERE id = %s"
        data = (item_name, quantity, item_id)
        cursor.execute(query, data)
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[update_item error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def item_bought(item_id, bought):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "UPDATE shopping_list SET bought = %s WHERE id = %s"
        data = (bought, item_id)
        cursor.execute(query, data)
        connection.commit()
        print("Item:", item_id, "Bought:", bought)
        return {"success": True}
    except Exception as e:
        print(f"[item_bought error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def low_stock_items(user_id):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "SELECT i.name, i.default_quantity, inv.quantity FROM inventory inv JOIN item i ON inv.item_id = i.id WHERE inv.user_id = %s AND inv.quantity <= i.default_quantity / 10"
        data = (user_id,)
        cursor.execute(query, data)
        items = cursor.fetchall()
        return {"success": True, "data": items}
    except Exception as e:
        print(f"[low_stock_items error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def remove_item(item_id):
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM shopping_list WHERE id = %s", (item_id,))
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[remove_item error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def clear_items(user_id):
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM shopping_list WHERE user_id = %s", (user_id,))
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[clear_items error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()
