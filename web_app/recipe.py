from database import database

class Recipe(database):
    def __init__(self):
        super().__init__()

    def get_recipes(self, user_only = False, user_id = None):
        cursor = self.connection.cursor()
        query = "SELECT id, name, instructions FROM recipe WHERE user_id = %s"
        if (not user_only):
            query += " OR user_id IS NULL;"
        data = (user_id,)
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
    
    def get_recipe_tools(self, recipe_id):
        cursor = self.connection.cursor()
        query = "SELECT tool_id FROM recipe_tool WHERE user_id = %s"
        data = (recipe_id,)
        cursor.execute(query, data)
        tool_ids = cursor.fetchall()
        cursor.close()
        # formats each id into a list
        tool_ids = [id[0] for id in tool_ids]
        return tool_ids

    # returns a list of any tools required for a recipe that a user doesn't own
    def get_missing_tools(self, recipe_tools, user_tools):
        return list(set(recipe_tools) - set(user_tools))
