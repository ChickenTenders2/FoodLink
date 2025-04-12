import mariadb

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
