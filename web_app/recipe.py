from database import database

class Recipe(database):
    def __init__(self):
        super().__init__()

    def get_recipes(self, search_term, page, user_id, user_only):
        limit = 10
        offset = (page - 1) * limit
        cursor = self.connection.cursor()
        query = f"""SELECT id, name, servings, prep_time, cook_time, instructions, user_id FROM recipe 
                    WHERE
                        {"MATCH(name) AGAINST (? IN NATURAL LANGUAGE MODE) AND" if search_term else ""}
                        user_id = ?
                        {"OR user_id IS NULL" if not user_only else ""} 
                        ORDER BY id DESC LIMIT ? OFFSET ?;
                """
        if search_term:
            data = (search_term, user_id, limit, offset)
        else:
            data = (user_id, limit, offset)
        cursor.execute(query, data)
        recipes = cursor.fetchall()
        cursor.close()
        return recipes
    
    def remove_recipe(self, recipe_id):
        cursor = self.connection.cursor()
        query = "DELETE FROM recipe WHERE id = %s;"
        data = (recipe_id,)
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()
    
    def edit_recipe(self, recipe_id, name, instructions):
        cursor = self.connection.cursor()
        query = """UPDATE recipe SET 
                    name = %s,
                    instructions = %s
                WHERE recipe_id = %s"""
        data = (name, instructions, recipe_id)
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()
    
    def get_recipe_tools(self, recipe_id):
        cursor = self.connection.cursor()
        query = "SELECT tool_id FROM recipe_tool WHERE recipe_id = %s"
        data = (recipe_id,)
        cursor.execute(query, data)
        tool_ids = cursor.fetchall()
        cursor.close()
        # formats each id into a list
        tool_ids = [id[0] for id in tool_ids]
        return tool_ids

    def get_recipe_items(self, recipe_id):
        cursor = self.connection.cursor()
        query = "SELECT item_name, quantity, unit FROM FoodLink.recipe_items WHERE recipe_id = %s;"
        data = (recipe_id,)
        cursor.execute(query, data)
        items = cursor.fetchall()
        cursor.close()
        items = [list(item) for item in items]
        return items
    
    # returns the best match for an ingredient that a user has in their inventory
    # returns the first item that fully matches the item name, are in the users inventory, and are in date
    def strict_search(self, user_id, item_name, quantity_threshold):
        cursor = self.connection.cursor()
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
            SELECT inv.id, i.name, i.brand, quantity, i.unit, expiry_date
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
        cursor.close()
        return item


