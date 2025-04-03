import mariadb

class database():
    def __init__(self):
        self.connection = self.connect()

    # returns db connection
    def connect(self):
        return mariadb.connect(
            host = "80.0.43.124",
            user = "FoodLink",
            password = "Pianoconclusiontown229!",
            database = "FoodLink"
        )
