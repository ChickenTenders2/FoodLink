from database import database

class inventory(database):
    def __init__(self):
        super().__init__()

    def get_items(self, user_id):
        cursor = self.connection.cursor()
        query = "SELECT inv.id, i.id, i.name, i.brand, quantity, i.unit, expiry_date, i.default_quantity FROM FoodLink.inventory inv JOIN FoodLink.item i ON (inv.item_id = i.id) WHERE inv.user_id = %s;"
        data = (user_id,)
        cursor.execute(query, data)
        items = cursor.fetchall()
        cursor.close()
        return items

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

    def update_item(self, inventory_id, quantity, expiry_date):
        cursor = self.connection.cursor()
        query = "UPDATE inventory SET quantity = %s, expiry_date = %s WHERE id = %s;"
        data = [quantity, expiry_date, inventory_id]
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()

    def search_items(self, user_id, search_term):
        cursor = self.connection.cursor()
        # search query uses full text for relevance based searching of items
        query = "SELECT inv.id, i.id, i.name, i.brand, quantity, i.unit, expiry_date, i.default_quantity FROM FoodLink.inventory inv JOIN FoodLink.item i ON inv.item_id = i.id WHERE (inv.user_id = %s AND MATCH(i.name) AGAINST (%s IN NATURAL LANGUAGE MODE));"
        data = (user_id, search_term)
        cursor.execute(query, data)
        items = cursor.fetchall()
        cursor.close()
        return items
