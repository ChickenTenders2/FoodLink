import mariadb
from datetime import date

class database():
    def __init__(self):
        self.connection = self.connect()

    # returns db connection
    def connect(self):
        return mariadb.connect(
            host = "81.109.118.20",
            user = "FoodLink",
            password = "Pianoconclusiontown229!",
            database = "FoodLink"
        )

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
    
    # def update_expiry(self, inventory_id, expiry_date):    
    #     cursor = self.connection.cursor()
    #     query = "UPDATE inventory SET expiry_date = %s WHERE id = %s;"
    #     data = [expiry_date, inventory_id]
    #     cursor.execute(query, data)
    #     self.connection.commit()
    #     cursor.close()

    def update_item(self, inventory_id, quantity, expiry_date):
        cursor = self.connection.cursor()
        query = "UPDATE inventory SET quantity = %s, expiry_date = %s WHERE id = %s;"
        data = [quantity, expiry_date, inventory_id]
        cursor.execute(query, data)
        self.connection.commit()
        cursor.close()
    
    def search_items(self, user_id, search_term):
        cursor = self.connection.cursor()
        #query = "SELECT inv.id, i.id, i.name, i.brand, quantity, i.unit, expiry_date, i.default_quantity FROM FoodLink.inventory inv JOIN FoodLink.item i ON (inv.item_id = i.id) WHERE inv.user_id = ? AND i.name LIKE ?"

        # search query uses full text for relevance based searching of items
        query = "SELECT inv.id, i.id, i.name, i.brand, quantity, i.unit, expiry_date, i.default_quantity FROM FoodLink.inventory inv JOIN FoodLink.item i ON inv.item_id = i.id WHERE (inv.user_id = %s AND MATCH(i.name) AGAINST (%s IN NATURAL LANGUAGE MODE));"
        data = (user_id, search_term)
        cursor.execute(query, data)
        items = cursor.fetchall()
        cursor.close()
        return items

    # def sort_items(self, user_id, sort_by):
    #     cursor = self.connection.cursor()
    #     query = "SELECT inv.id, i.id, i.name, i.brand, quantity, i.unit, expiry_date, i.default_quantity FROM FoodLink.inventory inv JOIN FoodLink.item i ON (inv.item_id = i.id) WHERE inv.user_id = ?"
    #     if sort_by == 'name':
    #         query += " ORDER BY i.name ASC"
    #     elif sort_by == 'expiry':
    #         query += " ORDER BY expiry_date ASC"
    #     cursor.execute(query, [user_id])
    #     items = cursor.fetchall()
    #     cursor.close()
    #     items = [list(i) for i in items]
    #     return items