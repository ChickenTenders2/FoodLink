from database import connection
import logging

def get_all():
    cursor = None
    try:
        cursor = connection.cursor()
        query = "SELECT id, name, servings, prep_time, cook_time, instructions FROM recipe WHERE user_id IS NULL;"
        cursor.execute(query)
        recipes = cursor.fetchall()
        return {"success": True, "recipes": recipes}
    except Exception as e:
        logging.error(f"[admin_recipe.get_all error] {e}")
        return {"success": False, "error": f"[admin_recipe.get_all error] {e}"}
    finally:
        if cursor:
            cursor.close()

def remove_recipe(id):
    cursor = None
    try:
        cursor = connection.cursor()
        query1 = "DELETE FROM recipe WHERE id = %s;"
        # one item tuple
        data1 = (id,)
        cursor.execute(query1, data1)
        query2 = "DELETE FROM recipe_items WHERE recipe_id = %s;"
        # one item tuple
        data2 = (id,)
        cursor.execute(query2, data2)
        query3 = "DELETE FROM recipe_tool WHERE recipe_id = %s;"
        # one item tuple
        data3 = (id,)
        cursor.execute(query3, data3)
        connection.commit()
        return {"success": True}
    except Exception as e:
        connection.rollback()
        logging.error(f"[admin_recipe.remove_recipe error] {e}")
        return {"success": False, "error": f"[admin_recipe.remove_recipe error] {e}"}
    finally:
        if cursor:
            cursor.close()

def update_recipe(recipe_id, name, serv, prep, cook, instructions, user_id = None):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "UPDATE FoodLink.recipe SET name = %s, servings = %s, prep_time = %s, cook_time = %s, instructions = %s, user_id = %s WHERE id = %s;"
        data = [name, serv, prep, cook, instructions, user_id, recipe_id]
        cursor.execute(query, data)
        connection.commit()
        return {"success": True}
    except Exception as e:
        connection.rollback()
        logging.error(f"[admin_recipe.update_recipe error] {e}")
        return {"success": False, "error": f"[admin_recipe.update_recipe error] {e}"}
    finally:
        if cursor:
            cursor.close()

def add_recipe(name, serv, prep, cook, instructions, user_id = None):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "INSERT INTO FoodLink.recipe (name, servings, prep_time, cook_time, instructions, user_id) VALUES (%s, %s, %s, %s, %s, %s);"
        data = [name, serv, prep, cook, instructions, user_id]
        print(data)
        cursor.execute(query, data)
        connection.commit()
        return {"success": True}
    except Exception as e:
        connection.rollback()
        logging.error(f"[admin_recipe.add_recipe error] {e}")
        return {"success": False, "error": f"[admin_recipe.add_recipe error] {e}"}
    finally:
        if cursor:
            cursor.close()

def update_recipe_ingredients(recipe_id, names, units, quantities):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "DELETE FROM recipe_items WHERE recipe_id = %s"
        data = (recipe_id, )
        cursor.execute(query, data)
        
        for name, unit, quantity in zip(names, units, quantities):
            cursor = connection.cursor()
            query = "INSERT INTO recipe_items (recipe_id, item_name, unit, quantity) VALUES (%s, %s, %s, %s);"
            data = [recipe_id, name, unit, quantity]
            cursor.execute(query, data)
        # only commits after completely updated
        connection.commit()
        return {"success": True}
    except Exception as e:
        connection.rollback()
        logging.error(f"[admin_recipe.update_recipe_ingredients error] {e}")
        return {"success": False, "error": f"[admin_recipe.update_recipe_ingredients error] {e}"}
    finally:
        if cursor:
            cursor.close()

def add_recipe_ingredients(recipe_id, names, units, quantities):
    cursor = None
    try:
        cursor = connection.cursor()
        for name, unit, quantity in zip(names, units, quantities):
            cursor = connection.cursor()
            query = "INSERT INTO recipe_items (recipe_id, item_name, unit, quantity) VALUES (%s, %s, %s, %s);"
            data = [recipe_id, name, unit, quantity]
            cursor.execute(query, data)
        # only commits after completely updated
        connection.commit()
        return {"success": True}
    except Exception as e:
        connection.rollback()
        logging.error(f"[admin_recipe.add_recipe_ingredients error] {e}")
        return {"success": False, "error": f"[admin_recipe.add_recipe_ingredients error] {e}"}
    finally:
        if cursor:
            cursor.close()

def get_id():
    cursor = None
    try:
        cursor = connection.cursor()
        query = "SELECT MAX(id) from FoodLink.recipe;"
        cursor.execute(query)
        id = cursor.fetchone()
        print(id)
        connection.commit()
        return {"success": True, "id": id}
    except Exception as e:
        connection.rollback()
        logging.error(f"[admin_recipe.get_id error] {e}")
        return {"success": False, "error": f"[admin_recipe.get_id error] {e}"}
    finally:
        if cursor:
            cursor.close()

def update_recipe_tools(recipe_id, tool_ids):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "DELETE FROM recipe_tool WHERE recipe_id = %s"
        data = (recipe_id, )
        cursor.execute(query, data)
        
        for tool in tool_ids:
            cursor = connection.cursor()
            query = "INSERT INTO recipe_tool (recipe_id, tool_id) VALUES (%s, %s);"
            data = [recipe_id, tool]
            cursor.execute(query, data)
            
        connection.commit()
        return {"success": True}
    except Exception as e:
        connection.rollback()
        logging.error(f"[admin_recipe.update_recipe_tools error] {e}")
        return {"success": False, "error": f"[admin_recipe.update_recipe_tools error] {e}"}
    finally:
        if cursor:
            cursor.close()

def add_recipe_tools(recipe_id, tool_ids):
    cursor = None
    try:
        cursor = connection.cursor()
        for tool in tool_ids:
            cursor = connection.cursor()
            query = "INSERT INTO recipe_tool (recipe_id, tool_id) VALUES (%s, %s);"
            data = [recipe_id, tool]
            cursor.execute(query, data)

        connection.commit()
        return {"success": True}
    except Exception as e:
        connection.rollback()
        logging.error(f"[admin_recipe.add_recipe_tools error] {e}")
        return {"success": False, "error": f"[admin_recipe.add_recipe_tools error] {e}"}
    finally:
        if cursor:
            cursor.close()
