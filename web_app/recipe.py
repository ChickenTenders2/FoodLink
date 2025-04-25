from database import connection

def get_recipes(search_term, page, user_id, user_only):
    cursor = None
    try:
        cursor = connection.cursor()
        limit = 10
        offset = (page - 1) * limit
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
        return {"success": True, "data": recipes}
    except Exception as e:
        print(f"[get_recipes error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def get_recipe(recipe_id):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "SELECT id, name, servings, prep_time, cook_time, instructions, user_id FROM recipe WHERE id = %s"
        data = (recipe_id,)
        cursor.execute(query, data)
        recipe = cursor.fetchone()
        return {"success": True, "data": recipe}
    except Exception as e:
        print(f"[get_recipe error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def remove_recipe(recipe_id):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "DELETE FROM recipe WHERE id = %s;"
        data = (recipe_id,)
        cursor.execute(query, data)
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[remove_recipe error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def remove_recipe_tools(recipe_id):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "DELETE FROM recipe_tool WHERE recipe_id = %s;"
        data = (recipe_id,)
        cursor.execute(query, data)
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[remove_recipe_tools error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def remove_recipe_items(recipe_id):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "DELETE FROM recipe_items WHERE recipe_id = %s;"
        data = (recipe_id,)
        cursor.execute(query, data)
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[remove_recipe_items error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def add_recipe(name, servings, prep_time, cook_time, instructions, user_id):
    cursor = None
    try:
        cursor = connection.cursor()
        query = """INSERT INTO recipe (name, servings, prep_time, cook_time, instructions, user_id) 
                    VALUES (%s, %s, %s, %s, %s, %s);"""
        data = (name, servings, prep_time, cook_time, instructions, user_id)
        cursor.execute(query, data)
        connection.commit()
        # gets id of the recipe inserted
        recipe_id = cursor.lastrowid
        return {"success": True, "data": recipe_id}
    except Exception as e:
        print(f"[add_recipe error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def edit_recipe(recipe_id, name, servings, prep_time, cook_time, instructions):
    cursor = None
    try:
        cursor = connection.cursor()
        query = """UPDATE recipe SET 
                    name = %s,
                    servings = %s,
                    prep_time = %s,
                    cook_time = %s,
                    instructions = %s
                WHERE id = %s"""
        data = (name, servings, prep_time, cook_time, instructions, recipe_id)
        cursor.execute(query, data)
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[edit_recipe error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def edit_recipe_tools(recipe_id, tool_ids):
    cursor = None
    try:
        cursor = connection.cursor()
        # removes all tools so any unselected options are removed
        query = "DELETE FROM recipe_tool WHERE recipe_id = %s;"
        data = (recipe_id,)
        cursor.execute(query, data)

        # stops inserting tools if none were selected
        if not tool_ids:
            return {"success": True}

        query = "INSERT INTO recipe_tool (recipe_id, tool_id) VALUES (%s, %s);"
        # creates list of the data needed to execute each query for storing recipe tools
        data = [(recipe_id, tool_id) for tool_id in tool_ids]
        # executes all queries
        cursor.executemany(query, data)
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[edit_recipe_tools error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def edit_recipe_items(recipe_id, items):
    cursor = None
    try:
        cursor = connection.cursor()
        # removes all items so any unselected options are removed
        query = "DELETE FROM recipe_items WHERE recipe_id = %s;"
        data = (recipe_id,)
        cursor.execute(query, data)

        # stops inserting items if none were selected
        if not items:
            return {"success": True}

        query = "INSERT INTO recipe_items (recipe_id, item_name, quantity, unit) VALUES (%s, %s, %s, %s);"
        # creates list of the data needed to execute each query for storing recipe items
        data = [(recipe_id, item_name, quantity, unit) for item_name, quantity, unit in items]
        # executes all queries
        cursor.executemany(query, data)
        connection.commit()
        return {"success": True}
    except Exception as e:
        print(f"[edit_recipe_items error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def get_recipe_tools(recipe_id):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "SELECT tool_id FROM recipe_tool WHERE recipe_id = %s"
        data = (recipe_id,)
        cursor.execute(query, data)
        tool_ids = cursor.fetchall()
        connection.commit()
        # formats each id into a list
        tool_ids = [id[0] for id in tool_ids]
        return {"success": True, "data": tool_ids}
    except Exception as e:
        print(f"[get_recipe_tools error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

def get_recipe_items(recipe_id):
    cursor = None
    try:
        cursor = connection.cursor()
        query = "SELECT item_name, quantity, unit FROM FoodLink.recipe_items WHERE recipe_id = %s;"
        data = (recipe_id,)
        cursor.execute(query, data)
        items = cursor.fetchall()
        connection.commit()
        items = [list(item) for item in items]
        return {"success": True, "data": items}
    except Exception as e:
        print(f"[get_recipe_items error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()

# returns the best match for an ingredient that a user has in their inventory
# returns the first item that fully matches the item name, are in the users inventory, and are in date
def strict_search(user_id, item_name, quantity_threshold):
    cursor = None
    try:
        cursor = connection.cursor()
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
        # if item is returned format date for frontend
        if item:
            item = list(item)
            item[6] = item[6].strftime('%Y-%m-%d')
        return {"success": True, "data": item}
    except Exception as e:
        print(f"[strict_search error] {e}")
        return {"success": False, "error": "An internal error occurred."}
    finally:
        if cursor:
            cursor.close()
