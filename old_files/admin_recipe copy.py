from database import database

class admin_recipe(database):
    def __init__(self):
        super().__init__()

    def get_all(self):
        cursor = self.connection.cursor()
        query = "SELECT id, name, servings, prep_time, cook_time, instructions FROM FoodLink.recipe WHERE user_id IS null;"
        cursor.execute(query)
        items = cursor.fetchall()
        cursor.close()
        return items

    def update_recipe(self, recipe_id, name, serv, prep, cook, instructions, user_id = None):
        cursor = self.connection.cursor()
        query = "UPDATE FoodLink.recipe SET name = %s, servings = %s, prep_time = %s, cook_time = %s, instructions = %s, user_id = %s WHERE id = %s;"
        data = [name, serv, prep, cook, instructions, user_id, recipe_id]
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    def add_recipe(self, name, serv, prep, cook, instructions, user_id = None):
        cursor = self.connection.cursor()
        query = "INSERT INTO FoodLink.recipe (name, servings, prep_time, cook_time, instructions, user_id) VALUES (%s, %s, %s, %s, %s, %s);"
        data = [name, serv, prep, cook, instructions, user_id]
        print(data)
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    def update_recipe_ingredients(self, recipe_id, names, units, quantities):

        cursor = self.connection.cursor()
        query = "DELETE FROM recipe_items WHERE recipe_id = %s"
        data = (recipe_id, )
        cursor.execute(query, data)
        self.connection.commit()
        
        for name, unit, quantity in zip(names, units, quantities):
            cursor = self.connection.cursor()
            query = "INSERT INTO recipe_items (recipe_id, item_name, unit, quantity) VALUES (%s, %s, %s, %s);"
            data = [recipe_id, name, unit, quantity]
            cursor.execute(query, data)
            self.connection.commit()
            cursor.close()

    def add_recipe_ingredients(self, recipe_id, names, units, quantities):
        for name, unit, quantity in zip(names, units, quantities):
            cursor = self.connection.cursor()
            query = "INSERT INTO recipe_items (recipe_id, item_name, unit, quantity) VALUES (%s, %s, %s, %s);"
            data = [recipe_id, name, unit, quantity]
            cursor.execute(query, data)
            self.connection.commit()
            cursor.close() 

    def update_recipe_tools(self, recipe_id, tool_ids):

        cursor = self.connection.cursor()
        query = "DELETE FROM recipe_tool WHERE recipe_id = %s"
        data = (recipe_id, )
        cursor.execute(query, data)
        self.connection.commit()
        
        for tool in tool_ids:
            cursor = self.connection.cursor()
            query = "INSERT INTO recipe_tool (recipe_id, tool_id) VALUES (%s, %s);"
            data = [recipe_id, tool]
            cursor.execute(query, data)
            self.connection.commit()
            cursor.close()

    def add_recipe_tools(self, recipe_id, tool_ids):
        for tool in tool_ids:
            cursor = self.connection.cursor()
            query = "INSERT INTO recipe_tool (recipe_id, tool_id) VALUES (%s, %s);"
            data = [recipe_id, tool]
            cursor.execute(query, data)
            self.connection.commit()
            cursor.close()

    def get_id(self):
        cursor = self.connection.cursor()
        query = "SELECT MAX(id) from FoodLink.recipe;"
        cursor.execute(query)
        id = cursor.fetchone()
        print(id)
        self.connection.commit()
        return id
    
    def remove_recipe(self, id):
        cursor = self.connection.cursor()
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
        self.connection.commit()
        cursor.close()