import mariadb

# shared connection for entire app
connection = mariadb.connect(
    host = "81.109.118.20",
    user = "FoodLink",
    password = "Pianoconclusiontown229!",
    database = "FoodLink"
)
