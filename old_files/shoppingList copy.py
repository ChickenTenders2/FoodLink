from database import database

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
    
    def add_items(self, user_id, items):
        cursor = self.connection.cursor()
        data = [(user_id, item[0], item[1]) for item in items]
        query = "INSERT INTO shopping_list (user_id, item_name, quantity) VALUES (?, ?, ?)"
        cursor.executemany(query, data)
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

    def low_stock_items(self, user_id):
        cursor = self.connection.cursor()
        query = "SELECT i.name, i.default_quantity, inv.quantity FROM inventory inv JOIN item i ON inv.item_id = i.id WHERE inv.user_id = %s AND inv.quantity <= i.default_quantity / 10"
        data = (user_id,)
        cursor.execute(query, data)
        items = cursor.fetchall()
        cursor.close()
        return items

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