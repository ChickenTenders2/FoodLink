from database import get_cursor, commit, safe_rollback
import logging
import json

def get_recipes(search_term, page, user_id, user_only):
    cursor = None
    limit = 10
    try:
        offset = (int(page) - 1) * limit
        cursor = get_cursor()
        query = f"""SELECT id, name, servings, prep_time, cook_time, instructions, user_id FROM recipe 
                    WHERE
                        {"MATCH(name) AGAINST (%s IN NATURAL LANGUAGE MODE) AND" if search_term else ""}
                        (user_id = %s
                        {"OR user_id IS NULL" if not user_only else ""}) 
                        ORDER BY id DESC LIMIT %s OFFSET %s
                """
        if search_term:
            data = (search_term, user_id, limit, offset)
        else:
            data = (user_id, limit, offset)
        cursor.execute(query, data)
        recipes = cursor.fetchall()
        return {"success": True, "recipes": recipes}
    except Exception as e:
        logging.error(f"[get_recipes error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def get_recipe(recipe_id):
    cursor = None
    try:
        cursor = get_cursor()
        query = "SELECT id, name, servings, prep_time, cook_time, instructions, user_id FROM recipe WHERE id = %s"
        data = (recipe_id,)
        cursor.execute(query, data)
        recipe = cursor.fetchone()
        return {"success": True, "recipe": recipe}
    except Exception as e:
        logging.error(f"[get_recipe error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def remove_recipe(recipe_id, user_id=None):
    ## if user submitted, make sure theyre deleting their own recipe
    if user_id:
        result = owner_check(recipe_id, user_id)
        if not result.get("success"):
            return result
    cursor = None
    try:
        cursor = get_cursor()
        # remove from recipe table
        query = "DELETE FROM recipe WHERE id = %s;"
        data = (recipe_id,)
        cursor.execute(query, data)
        # remove recipe tools
        query = "DELETE FROM recipe_tool WHERE recipe_id = %s;"
        data = (recipe_id,)
        cursor.execute(query, data)
        # remove recipe items
        query = "DELETE FROM recipe_items WHERE recipe_id = %s;"
        data = (recipe_id,)
        cursor.execute(query, data)

        commit()
        return {"success": True}
    except Exception as e:
        safe_rollback()
        logging.error(f"[remove_recipe error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def process_form(action, form, user_id):
    recipe_id = form.get("recipe_id")
    name = form.get("name")
    servings = form.get("servings")
    prep_time = form.get("prep_time")
    cook_time = form.get("cook_time")
    instructions = form.get("instructions")

    # if any information not entered
    if not (name and servings and prep_time and cook_time and instructions):
        return {"success": False, "error": "Form value(s) were missing."}
    
    ingredients_string = form.get("ingredients")
    tool_ids_string = form.get("tool_ids")

    # list variables must be stringified client side so lists transfer correctly
    # they are so decoded to get original data type back
    ingredients = json.loads(ingredients_string)
    tool_ids = json.loads(tool_ids_string)

    if not (ingredients or tool_ids):
        return {"success": False, "error": "Ingredients or tools were empty."}

    action(recipe_id, name, servings, prep_time, cook_time, instructions, ingredients, tool_ids, user_id)

def add_recipe(name, servings, prep_time, cook_time, instructions, items, tool_ids, user_id):
    cursor = None
    try:
        cursor = get_cursor()
        # adds to recipe table
        query = """INSERT INTO recipe (name, servings, prep_time, cook_time, instructions, user_id) 
                VALUES (%s, %s, %s, %s, %s, %s);"""
        data = (name, servings, prep_time, cook_time, instructions, user_id)
        cursor.execute(query, data)
        # gets id of the recipe inserted
        recipe_id = cursor.lastrowid

        edit_recipe_tools(cursor, recipe_id, tool_ids)
        edit_recipe_items(cursor, recipe_id, items)
        commit()
        return {"success": True, "recipe_id": recipe_id}
    except Exception as e:
        safe_rollback()
        logging.error(f"[add_recipe error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def edit_recipe(cursor, recipe_id, name, servings, prep_time, cook_time, instructions, items, tool_ids, user_id=None):
    ## if user submitted, make sure theyre editing their own recipe
    if user_id:
        result = owner_check(recipe_id, user_id)
        if not result.get("success"):
            return result
    cursor = None
    try:
        cursor = get_cursor()
        # updates recipe table
        query = """UPDATE recipe SET 
                name = %s,
                servings = %s,
                prep_time = %s,
                cook_time = %s,
                instructions = %s
            WHERE id = %s"""
        data = (name, servings, prep_time, cook_time, instructions, recipe_id)
        cursor.execute(query, data)

        edit_recipe_tools(cursor, recipe_id, tool_ids)
        edit_recipe_items(cursor, recipe_id, items)
        commit()
        return {"success": True}
    except Exception as e:
        safe_rollback()
        logging.error(f"[add_recipe error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()
        
def edit_recipe_tools(cursor, recipe_id, tool_ids):
    # removes all tools so any unselected options are removed
    query = "DELETE FROM recipe_tool WHERE recipe_id = %s;"
    data = (recipe_id,)
    cursor.execute(query, data)

    query = "INSERT INTO recipe_tool (recipe_id, tool_id) VALUES (%s, %s);"
    # creates list of the data needed to execute each query for storing recipe tools
    data = [(recipe_id, tool_id) for tool_id in tool_ids]
    # executes all queries
    cursor.executemany(query, data)

def edit_recipe_items(cursor, recipe_id, items):
    # removes all items so any unselected options are removed
    query = "DELETE FROM recipe_items WHERE recipe_id = %s;"
    data = (recipe_id,)
    cursor.execute(query, data)

    query = "INSERT INTO recipe_items (recipe_id, item_name, quantity, unit) VALUES (%s, %s, %s, %s);"
    # creates list of the data needed to execute each query for storing recipe items
    data = [(recipe_id, item_name, quantity, unit) for item_name, quantity, unit in items]
    # executes all queries
    cursor.executemany(query, data)

# checks if user is modifying their own recipe
def owner_check(id, user_id):
    cursor = None
    try:
        cursor = get_cursor()
        cursor.execute("SELECT user_id FROM recipe WHERE id = %s;", (id,))
        result = cursor.fetchone()
        if not result or result[0] != user_id:
            return {"success": False, "error": "Permission denied."}
        return {"success": True}
    except Exception as e:
        logging.error(f"[recipe.owner_check error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()


def get_recipe_tools(recipe_id):
    cursor = None
    try:
        cursor = get_cursor()
        query = "SELECT tool_id FROM recipe_tool WHERE recipe_id = %s"
        data = (recipe_id,)
        cursor.execute(query, data)
        tool_ids = cursor.fetchall()
        # formats each id into a list
        tool_ids = [id[0] for id in tool_ids]
        return {"success": True, "tool_ids": tool_ids}
    except Exception as e:
        logging.error(f"[get_recipe_tools error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def get_recipe_items(recipe_id):
    cursor = None
    try:
        cursor = get_cursor()
        query = "SELECT item_name, quantity, unit FROM FoodLink.recipe_items WHERE recipe_id = %s;"
        data = (recipe_id,)
        cursor.execute(query, data)
        items = cursor.fetchall()
        items = [list(item) for item in items]
        return {"success": True, "items": items}
    except Exception as e:
        logging.error(f"[get_recipe_items error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()
