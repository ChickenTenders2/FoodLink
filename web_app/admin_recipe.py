from database import connection

def get_all():
    cursor = None
    try:
        cursor = connection.cursor()
        query = "SELECT id, name, servings, prep_time, cook_time, instructions FROM recipe WHERE user_id IS NULL;"
        cursor.execute(query)
        recipes = cursor.fetchall()
        return {"success": True, "data": recipes}
    except Exception as e:
        print(f"[get_all error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def remove_recipe(recipe_id):
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM recipe WHERE id = %s;", (recipe_id,))
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[remove_recipe error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def update_recipe(recipe_id, name, servings, prep_time, cook_time, instructions):
    cursor = None
    try:
        cursor = connection.cursor()
        query = """
            UPDATE recipe
            SET name = %s, servings = %s, prep_time = %s, cook_time = %s, instructions = %s
            WHERE id = %s;
        """
        cursor.execute(query, (name, servings, prep_time, cook_time, instructions, recipe_id))
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[update_recipe error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def add_recipe(name, servings, prep_time, cook_time, instructions):
    cursor = None
    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO recipe (name, servings, prep_time, cook_time, instructions)
            VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(query, (name, servings, prep_time, cook_time, instructions))
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[add_recipe error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def update_recipe_ingredients(recipe_id, names, units, quantities):
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM recipe_items WHERE recipe_id = %s;", (recipe_id,))
        query = "INSERT INTO recipe_items (recipe_id, item_name, quantity, unit) VALUES (%s, %s, %s, %s);"
        data = [(recipe_id, names[i], quantities[i], units[i]) for i in range(len(names))]
        cursor.executemany(query, data)
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[update_recipe_ingredients error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def add_recipe_ingredients(recipe_id, names, units, quantities):
    return update_recipe_ingredients(recipe_id, names, units, quantities)

def get_id():
    cursor = None
    try:
        cursor = connection.cursor()
        query = "SELECT MAX(id) + 1 FROM recipe;"
        cursor.execute(query)
        result = cursor.fetchone()
        id = result[0]
        return {"success": True, "data": id}
    except Exception as e:
        print(f"[get_id error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def update_recipe_tools(recipe_id, tool_ids):
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM recipe_tool WHERE recipe_id = %s;", (recipe_id,))
        if tool_ids:
            query = "INSERT INTO recipe_tool (recipe_id, tool_id) VALUES (%s, %s);"
            data = [(recipe_id, tid) for tid in tool_ids]
            cursor.executemany(query, data)
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[update_recipe_tools error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def add_recipe_tools(recipe_id, tool_ids):
    return update_recipe_tools(recipe_id, tool_ids)
