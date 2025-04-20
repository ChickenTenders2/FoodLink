from database import database

class RecipeTable(database):
    def __init__(self):
        super().__init__()

    def get_all(self):
        cursor = self.connection.cursor()
        query = "SELECT id, name, servings, prep_time, cook_time, instructions FROM FoodLink.recipe WHERE user_id IS null;"
        cursor.execute(query)
        items = cursor.fetchall()
        cursor.close()
        return items

    def add_recipe(self, name, serv, prep, cook, instructions, user_id=None):
        print(name)
        print(instructions)
        cursor = self.connection.cursor()
        query = "INSERT INTO FoodLink.recipe (name, servings, prep_time, cook_time, instructions, user_id) VALUES (%s, %s, %s, %s, %s, %s);"
        data = (name, serv, prep, cook, instructions, user_id)
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    def remove_recipe(self, recipe_id):
        cursor = self.connection.cursor()
        query = "DELETE FROM recipe WHERE id = %s;"
        # one item tuple
        data = (recipe_id,) 
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    def update_recipe(self, recipe_id, name, serv, prep, cook, instructions, user_id = None):
        cursor = self.connection.cursor()
        query = "UPDATE FoodLink.recipe SET name = %s, servings = %s, prep_time = %s, cook_time = %s, instructions = %s, user_id = %s WHERE id = %s;"
        data = [name, serv, prep, cook, instructions, user_id, recipe_id]
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    def get_tools(self, id):
        cursor = self.connection.cursor()
        query = "SELECT rt.tool_id FROM FoodLink.recipe r JOIN FoodLink.recipe_tool rt ON rt.recipe_id = r.id WHERE r.id = %s;"
        data = (id,)
        cursor.execute(query, data)
        items = cursor.fetchall()
        cursor.close()
        return items
    
    def get_recipe_items(self, id):
        cursor = self.connection.cursor()
        query = "SELECT ri.item_name, ri.unit, ri.quantity FROM FoodLink.recipe r JOIN FoodLink.recipe_items ri ON ri.recipe_id = r.id WHERE r.id = %s;"
        data = (id,)
        cursor.execute(query, data)
        items = cursor.fetchall()
        cursor.close()
        return items
    
    

