import mariadb
from datetime import date

class database():
    def __init__(self):
        self.connection = self.connect()

    def connect(self):
        return mariadb.connect(
            host = "foodlink.ddns.net",
            user = "FoodLink",
            password = "Pianoconclusiontown229!",
            database = "FoodLink"
        )

class inventory(database):
    def __init__(self):
        super().__init__()

    def add_item(self, user_id, item_id, quantity, expiry_date):
        cursor = self.connection.cursor()
        query = "INSERT INTO inventory (user_id, item_id, quantity, expiry_date) VALUES (%s, %s, %s, %s);"
        data = (user_id, item_id, quantity, expiry_date)
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    def remove_item(self, inventory_id):
        cursor = self.connection.cursor()
        query = "DELETE FROM inventory WHERE id = %s;"
        # one item tuple
        data = (inventory_id,) 
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    def update_quantity(self, inventory_id, quantity):    
        cursor = self.connection.cursor()
        query = "UPDATE inventory SET quantity = %s WHERE id = %s;"
        data = [quantity, inventory_id]
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()
    
    def update_expiry(self, inventory_id, expiry_date):    
        cursor = self.connection.cursor()
        query = "UPDATE inventory SET expiry_date = %s WHERE id = %s;"
        data = [expiry_date, inventory_id]
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

if __name__ == "__main__":
    i = inventory()
    i.update_expiry(3, date(2025, 4, 2))
    
