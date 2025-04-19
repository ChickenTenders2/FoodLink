from database import database

class RecipeTable(database):
    def __init__(self):
        super().__init__()

    def get_all(self):
        cursor = self.connection.cursor()
        query = "SELECT * from recipe;"
        cursor.execute(query)
        items = cursor.fetchall()
        cursor.close()
        return items

    def add_recipe(self, name, instructions, user_id=None):
        print(name)
        print(instructions)
        cursor = self.connection.cursor()
        query = "INSERT INTO FoodLink.recipe (name, instructions, user_id) VALUES (%s, %s, %s);"
        data = (name, instructions, user_id)
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

    def update_recipe(self, recipe_id, name, instructions, user_id = None):
        cursor = self.connection.cursor()
        query = "UPDATE FoodLink.recipe SET name = %s, instructions = %s, user_id = %s WHERE id = %s;"
        data = [name, instructions, user_id, recipe_id]
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()
    

