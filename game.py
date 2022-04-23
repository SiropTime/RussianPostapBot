import sqlite3
from sqlite3 import Error

from emoji import emojize
from aiogram.utils import markdown as md

from instruments.game_utils import *
from instruments.player import Player
from instruments.utility import logger


class Game:
    def __init__(self):
        self.db = None
        self.locations = []
        self.animals = []
        self.players = {}

        try:
            self.db = sqlite3.connect("data.db")
            logger.info("Соединение с базой данных произошло успешно!")
        except Error as e:
            logger.error(f"При присоединении к БД произошла ошибка: '{e}'.")

        self.cursor = self.db.cursor()

        self.load_locations()
        self.load_animals()

        self.load_players()

    # Подготовка для вывода всех игроков, записанных в БД
    def prepare_players(self):
        players_msg = [emojize(":bar_chart: ***Холопы***:\n\n", use_aliases=True)]
        for id, p in self.players.items():
            msgs = p.prepare_profile()
            player_msg = emojize(":man: ***" + p.name + "*** id: " + md.code(str(id)) + "\n", use_aliases=True)
            player_msg += emojize(":black_square_button: ***Опыт***: " + str(p.xp) + "\n", use_aliases=True)
            player_msg += emojize(":black_square_button: ***Уровень***: " + str(p.level) + "\n", use_aliases=True)
            player_msg += emojize(":black_square_button: ***Локация***: " + p.location.name + "\n", use_aliases=True)
            player_msg += emojize(":black_square_button: ***Деньги***: " + str(p.money) + "\n", use_aliases=True)
            player_msg += "\n" + msgs[1]
            player_msg += "\n" + msgs[2]
            player_msg += "\n" + msgs[0]
            player_msg += "\n" + msgs[3]
            players_msg.append(player_msg)
        logger.info("Подготовлены игроки для вывода")
        return players_msg

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

    def update_players(self):
        for p in self.players.values():
            p.update_player(self.cursor, self.db)

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
            self.locations.append(loc)
        logger.info(self.locations)
        logger.info("Загрузка локаций завершена успешно")

    def update_locations(self):
        for loc in self.locations:
            self.cursor.execute("""
                                INSERT INTO locations VALUES (?, ?, ?, ?);
                                """,
                                (loc.name, loc.description, loc.coordinates[0], loc.coordinates[1]))
        self.db.commit()

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
        logger.info(self.animals)
        logger.info("Загрузка существ завершена успешно")

    def update_animals(self):
        for anim in self.animals:
            self.cursor.execute("""
                                INSERT INTO animals VALUES (?, ?, ?);
                                """, (anim.name, anim.description, anim.area))
        self.db.commit()
