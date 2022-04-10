import logging
import sqlite3
from sqlite3 import Error

from instruments.game_utils import *
from instruments.player import Player


class Game:
    def __init__(self):
        self.db = None
        self.locations = []
        self.animals = []
        self.players = {}
        self.journal = ""

        # self.helper = RolePlayHelper()

        try:
            self.db = sqlite3.connect("data.db", check_same_thread=False)
            logging.info("Соединение с базой данных произошло успешно!")
        except Error as e:
            logging.error(f"При присоединении к БД произошла ошибка: '{e}'.")

        self.cursor = self.db.cursor()

        self.load_locations()
        self.load_animals()

        self.load_players()

    def create_player(self, id: int, name: str, biography: str, player: Player):
        player.id = id
        player.name = name
        player.biography = biography
        self.players[id] = player
        player.create_player(self.cursor, self.db)

    def load_players(self):
        self.cursor.execute("""
                            SELECT * FROM players;
                            """)
        players = self.cursor.fetchall()
        for p in players:
            player = Player()
            player.id = p[0]
            player.load_player(self.cursor, self)
            self.players[player.id] = player

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
        logging.info(self.locations)
        logging.info("Загрузка локаций завершена успешно")

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
        logging.info(self.animals)
        logging.info("Загрузка существ завершена успешно")
