from database import database

class item(database):
    def __init__(self):
        super().__init__()

    def barcode_search(self, user_id, barcode_number):
        cursor = self.connection.cursor()
        # search query uses full text for relevance based searching of items
        query = "SELECT id, name, brand, expiry_time, default_quantity, unit FROM FoodLink.item WHERE barcode = %s AND (user_id IS NULL OR user_id = %s);"
        data = (barcode_number, user_id)
        cursor.execute(query, data)
        items = cursor.fetchall()
        cursor.close()
        return items

    def text_search(self, user_id, search_term):
        cursor = self.connection.cursor()
        # search query uses full text for relevance based searching of items
        query = "SELECT * FROM FoodLink.item WHERE MATCH(name) AGAINST (%s IN NATURAL LANGUAGE MODE) AND (user_id IS NULL OR user_id = %s);"
        data = (search_term, user_id)
        cursor.execute(query, data)
        items = cursor.fetchall()
        cursor.close()
        return items
    
    def add_item(self, admin_id, barcode, name, brand, expiry_time, default_quantity, unit):
        cursor = self.connection.cursor()
        # search query uses full text for relevance based searching of items
        query = "INSERT INTO FoodLink.item (barcode, name, brand, expiry_time, default_quantity, unit) VALUES (%s, %s, %s, %s, %s, %s);"
        data = (search_term, user_id)
        cursor.execute(query, data)
        items = cursor.fetchall()
        cursor.close()
        return items

    