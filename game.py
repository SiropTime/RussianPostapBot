import sqlite3
from sqlite3 import Error
from game_utils import *


class Game:
    def __init__(self):
        self.db = None
        self.locations = []
        self.animals = []
        self.players = {}
        self.helper = RolePlayHelper()

        try:
            self.db = sqlite3.connect("data.db")
            print("Connection to SQLite DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")

        self.cursor = self.db.cursor()
        self.load_locations()

        self.player = Player()
        self.player.id = 1
        self.player.load_player(self.cursor)
        item = Item()
        item.name = "Патрон"
        item.quantity = 1
        item.description = "9мм"
        self.player.add_item_to_inventory(self.cursor, item)
        print(self.player.inventory)

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


class Player:
    def __init__(self):
        self.id = 0
        self.name = ""
        self.biography = ""
        self.inventory = []
        self.main_skills = {"Физподготовка": 0,
                            "Интеллект": 0,
                            "Восприятие": 0,
                            "Харизма": 0}
        self.add_skills = {"Длинное оружие": 0, "Короткое оружие": 0,
                           "Тяжёлое оружие": 0, "Лёгкое оружие": 0,
                           "Режущее оружие": 0, "Древковое оружие": 0,
                           "Дробящее оружие": 0, "Огнестрельное оружие": 0,
                           "Метательное оружие": 0, "Луки и арбалеты": 0,
                           "Взрывчатка": 0, "Ловушки": 0,
                           "Скрытность": 0, "Взлом": 0,
                           "Кража": 0, "Красноречие": 0,
                           "Общая эрудиция": 0, "Медицина": 0,
                           "Устойчивость": 0, "Боевые искусства": 0,
                           "Ремесло": 0, "Кузнечество": 0,
                           "Кожевничество": 0, "Строительство": 0,
                           "Технические знания": 0, "Психологическая устойчивость": 0,
                           "Сила": 0, "Ловкость": 0, "Выносливость": 0}
        self.status = {"Голова": 100, "Грудь": 100, "Живот": 100,
                       "Левая рука": 100, "Правая рука": 100,
                       "Левая нога": 100, "Правая нога": 100,
                       "Психологическая устойчивость": 100,
                       "Выносливость": 600, "Кровь": 4600}

    # Добавление предмета в базу данных инвентаря
    def add_item_to_inventory(self, cursor: sqlite3.Cursor, item: Item):
        self.inventory.append(item)
        cursor.execute("""
                        INSERT INTO inventory (player_id, item, quantity, description) VALUES
                        (?, ?, ?, ?)
                        """, (self.id, item.name, item.quantity, item.description))

    # Загружаем персонажа из базы данных
    def load_player(self, cursor: sqlite3.Cursor):
        # Подгружаем состояние персонажа
        self._load_status(cursor, self.id)
        self._load_inventory(cursor, self.id)
        self._load_main_skills(cursor, self.id)
        self._load_add_skills(cursor, self.id)

    def create_player(self):
        pass

    #
    #
    #
    # Вспомогательные функции для создания декомпозиции
    def _load_status(self, cursor: sqlite3.Cursor, id: int):
        cursor.execute("""
                               SELECT * FROM status where player_id = ?;
                               """, [id])
        status = cursor.fetchone()
        print(status)

        i = 1
        for stat in self.status.keys():
            self.status[stat] = status[i]
            i += 1

        print(self.status)
        print("Завершена загрузка состояния персонажа с id:", id)

    def _load_inventory(self, cursor: sqlite3.Cursor, id: int):
        cursor.execute("""
                                       SELECT * FROM inventory where player_id = ?;
                                       """, [id])
        inventory = cursor.fetchall()
        print(inventory)

        for i in range(len(inventory)):
            item = Item()
            item.name = inventory[i][1]
            item.quantity = inventory[i][2]
            item.description = inventory[i][3]
            self.inventory.append(item)
        print(self.inventory)
        print("Завершена загрузка инвентаря персонажа с id:", id)

    def _load_main_skills(self, cursor: sqlite3.Cursor, id: int):
        cursor.execute("""
                                               SELECT * FROM main_skills where player_id = ?;
                                               """, [id])
        main_skills = cursor.fetchone()
        print(main_skills)

        i = 1
        for skill in self.main_skills.keys():
            self.main_skills[skill] = main_skills[1]
            i += 1

        print(self.main_skills)
        print("Завершена загрузка основных навыков персонажа с id:", id)

    def _load_add_skills(self, cursor: sqlite3.Cursor, id: int):
        cursor.execute("""
                                                       SELECT * FROM add_skill where player_id = ?;
                                                       """, [id])
        add_skills = cursor.fetchone()
        print(add_skills)

        i = 1
        for skill in self.add_skills.keys():
            self.add_skills[skill] = add_skills[i]
            i += 1

        print(self.add_skills)
        print("Завершена загрузка дополнительных навыков навыков персонажа с id:", id)


class GameMaster:
    def __init__(self):
        pass


if __name__ == "__main__":
    game = Game()
