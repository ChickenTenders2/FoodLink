import mariadb

class database():
    def __init__(self):
        self.connection = self.connect()
