import sqlite3
from sqlite3 import Error

from instruments.game_utils import *


class Game:
    def __init__(self):
        self.db = None
        self.locations = []
        self.animals = []
        self.players = {}
        # self.helper = RolePlayHelper()

        try:
            self.db = sqlite3.connect("data.db")
            print("Соединение с базой данных произошло успешно!")
        except Error as e:
            print(f"При присоединении к БД произошла ошибка: '{e}'.")

        self.cursor = self.db.cursor()
        self.load_locations()

    def create_player(self, id: int, name: str, biography: str, player):
        player.id = id
        player.name = name
        player.biography = biography
        self.players[id] = player
        player.create_player(self.cursor, self.db)

    def load_locations(self):
        self.cursor.execute("""
                            SELECT * FROM locations;
                            """)
        locations = self.cursor.fetchall()
        for i in locations:
            loc = Location()
            loc.name = i[0]
            loc.description = i[1]
            loc.coordinates = (i[2], i[3])
            loc.neighbours = i[4]
            self.locations.append(loc)
        print(self.locations)
        print("Загрузка локаций завершена успешно")

    def load_animals(self):
        self.cursor.execute("""
                            SELECT * FROM animals;
                            """)
        animals = self.cursor.fetchall()
        for i in animals:
            animal = Animal()
            animal.name = i[0]
            animal.description = i[1]
            animal.area = i[2]
        print(self.animals)
        print("Загрузка существ завершена успешно")


class GameMaster:
    def __init__(self):
        pass


# if __name__ == "__main__":
#     game = Game()
