import mariadb

class database():
    def __init__(self):
        self.connection = self.connect()

    def connect(self):
        return mariadb.connect(
            host = "80.0.43.124",
            user = "FoodLink",
            password = "Pianoconclusiontown229!",
            database = "FoodLink"
        )

class shoppingList(database):
    def __init__(self):
        super().__init__()

    def get_items(self, user_id):
        cursor = self.connection.cursor()
        query = "SELECT id, item_name, quantity, bought FROM FoodLink.shopping_list WHERE user_id = %s;"
        data = (user_id,)
        cursor.execute(query, data)
        items = cursor.fetchall()
        cursor.close()
        return items

    def add_item(self, user_id, item_name, quantity):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO shopping_list (user_id, item_name, quantity) VALUES (?, ?, ?)", (user_id, item_name, quantity))
        self.connection.commit()
        cursor.close()
    
    def update_item(self, item_id, item_name, quantity):
        cursor = self.connection.cursor()
        query = "UPDATE shopping_list SET item_name = %s, quantity = %s WHERE id = %s"
        data = (item_name, quantity, item_id)
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    def item_bought(self, item_id, bought):
        cursor = self.connection.cursor()
        query = "UPDATE shopping_list SET bought = %s WHERE id = %s"
        data = (bought, item_id)
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()
        print("Item:", item_id, "Bought:", bought)

    def remove_item(self, item_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM shopping_list WHERE id = ?", (item_id,))
        self.connection.commit()
        cursor.close()

    def clear_items(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM shopping_list WHERE user_id = ?", (user_id,))
        self.connection.commit()
        cursor.close()