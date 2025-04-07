from database import database

class item_table(database):
    def __init__(self):
        super().__init__()

    def barcode_search(self, user_id, barcode_number):
        cursor = self.connection.cursor()
        # searches for an item by barcode
        query = "SELECT id, name, brand, expiry_time, default_quantity, unit FROM FoodLink.item WHERE barcode = %s AND (user_id IS NULL OR user_id = %s);"
        data = (barcode_number, user_id)
        cursor.execute(query, data)
        item = cursor.fetchall()
        cursor.close()
        return item

    def text_search(self, user_id, search_term):
        cursor = self.connection.cursor()
        # search query uses full text for relevance based searching of items
        query = "SELECT * FROM FoodLink.item WHERE MATCH(name) AGAINST (%s IN NATURAL LANGUAGE MODE) AND (user_id IS NULL OR user_id = %s);"
        data = (search_term, user_id)
        cursor.execute(query, data)
        items = cursor.fetchall()
        cursor.close()
        return items
    
    def add_item(self, barcode, name, brand, expiry_time, default_quantity, unit, user_id = None):
        cursor = self.connection.cursor()
        query = "INSERT INTO FoodLink.item (barcode, name, brand, expiry_time, default_quantity, unit, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s);"
        data = (barcode, name, brand, expiry_time, default_quantity, unit, user_id)
        cursor.execute(query, data)
        self.connection.commit()
        # gets id of the item inserted
        item_id = cursor.lastrowid
        cursor.close()
        return item_id