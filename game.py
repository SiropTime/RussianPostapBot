import sqlite3
from sqlite3 import Error

from emoji import emojize

from game_utils import *
from random import randint
import aiogram.utils.markdown as md


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

        # self.player = Player()
        # self.player.id = 1
        # self.player.load_player(self.cursor)
        # item = Item()
        # item.name = "Патрон"
        # item.quantity = 1
        # item.description = "9мм"
        # self.player.add_item_to_inventory(self.cursor, item)
        # print(self.player.inventory)

    def create_player(self, id: int, name: str, biography: str, player):
        player.id = id
        player.name = name
        player.biography = biography
        self.players[id] = player
        player._create_player(self.cursor, self.db)

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
        self.money = 0
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
        self.priority_skills = []
        self.status = {"Голова": 100, "Грудь": 100, "Живот": 100,
                       "Левая рука": 100, "Правая рука": 100,
                       "Левая нога": 100, "Правая нога": 100,
                       "Психологическая устойчивость": 100,
                       "Выносливость": 600, "Кровь": 4600}

    # Подготовка всех данных для вывода профиля
    def prepare_profile(self):
        main_chars_msg = md.text(md.underline(emojize(":clipboard: ***Профиль***", use_aliases=True)),
                                 "***Основные характеристики***:",
                                 emojize(":muscle: Физподготовка" + str(self.main_skills["Физподготовка"]), use_aliases=True),
                                 emojize(":brain: Интеллект" + str(self.main_skills["Интеллект"]), use_aliases=True),
                                 emojize(":eyes: Восприятие" + str(self.main_skills["Восприятие"]), use_aliases=True),
                                 emojize(":bust_in_silhouette: Харизма" + str(self.main_skills["Харизма"]), use_aliases=True),
                                 sep="\n")
        add_chars_msg = "Дополнительные характеристики\n"
        for k, v in self.add_skills.items():
            add_chars_msg += k + ": " + str(v)

        return [main_chars_msg, add_chars_msg]

    # Добавление предмета в базу данных инвентаря
    def add_item_to_inventory(self, cursor: sqlite3.Cursor, item: Item):
        self.inventory.append(item)
        cursor.execute("""
                        INSERT INTO inventory (player_id, item, quantity, description) VALUES
                        (?, ?, ?, ?)
                        """, (self.id, item.name, item.quantity, item.description))

    # Создаём персонажа и загружаем его в бд.
    #
    def _create_player(self, cursor: sqlite3.Cursor, connection: sqlite3.Connection):
        cursor.execute("""
                       INSERT INTO players (id, name, biography) VALUES (?, ?, ?);
                       """,
                       (self.id, self.name, self.biography))
        print(self.id, self.name, self.biography)
        print("Успешно загружен")
        connection.commit()

    def setup_main_skills(self, cursor: sqlite3.Cursor, connection: sqlite3.Connection):
        temp = [self.id]
        for i in self.main_skills.values():
            temp.append(i)
        print(temp)
        cursor.execute("""
                       INSERT INTO main_skills (player_id, physical, intelligence, perception, charisma)
                       VALUES (?, ?, ?, ?, ?);
                       """, tuple(temp))
        connection.commit()

    # Загружаем персонажа из базы данных
    def load_player(self, cursor: sqlite3.Cursor):
        # Подгружаем состояние персонажа
        self._load_player(cursor)
        self._load_status(cursor, self.id)
        self._load_inventory(cursor, self.id)
        self._load_main_skills(cursor, self.id)
        self._load_add_skills(cursor, self.id)

    # Расчёт дополнительных навыков
    def calculate_skills(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        self._calculate_physics()
        self._calculate_intelligence()
        self._calculate_perception()
        self.add_skills["Психологическая устойчивость"] = int(
            0.9 * self.add_skills["Устойчивость"] + 2 * self.main_skills["Интеллект"])
        for skill in self.priority_skills:
            self.add_skills[skill] = int(self.add_skills[skill] * 1.25)
        cursor.execute("""
                        INSERT INTO add_skill VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """, tuple([self.id] + [s for s in self.add_skills.values()]))
        conn.commit()

    def create_player(self):
        pass

    #
    #
    #
    # Вспомогательные функции для создания декомпозиции
    def _calculate_physics(self):
        self.add_skills["Выносливость"] = int((randint(1000, 3500) * 0.001) * self.main_skills["Физподготовка"])
        self.add_skills["Ловкость"] = int((randint(1000, 3500) * 0.001) * self.main_skills["Физподготовка"])
        self.add_skills["Сила"] = int((randint(1000, 3500) * 0.001) * self.main_skills["Физподготовка"])
        self.add_skills["Боевые искусства"] = int(
            3 * self.main_skills["Физподготовка"] + 1.5 * self.main_skills["Восприятие"])
        self.add_skills["Устойчивость"] = int(
            2.5 * self.main_skills["Физподготовка"] + 2 * self.add_skills["Выносливость"])
        for k in self.add_skills.keys():
            if k == "Огнестрельное оружие":
                break
            self.add_skills[k] = int(2 * self.main_skills["Физподготовка"] + 1.4 * self.add_skills["Боевые искусства"])

    def _calculate_intelligence(self):
        self.add_skills["Взрывчатка"] = int(1.25 * self.main_skills["Интеллект"])
        self.add_skills["Ловушки"] = int(1.25 * self.main_skills["Интеллект"])
        self.add_skills["Красноречие"] = int(1.8 * self.main_skills["Интеллект"] + 2.15 * self.main_skills["Харизма"])
        self.add_skills["Общая эрудиция"] = int(4 * self.main_skills["Интеллект"])
        self.add_skills["Медицина"] = int(2 * self.main_skills["Интеллект"] + 1.5 * self.add_skills["Общая эрудиция"])
        self.add_skills["Ремесло"] = int(randint(1000, 3100) * 0.001 * self.main_skills["Интеллект"])
        self.add_skills["Кузнечество"] = int(
            randint(1000, 3100) * 0.001 * self.main_skills["Интеллект"] + 0.5 * self.add_skills["Ремесло"])
        self.add_skills["Кожевничество"] = int(
            randint(1000, 3100) * 0.001 * self.main_skills["Интеллект"] + 0.5 * self.add_skills["Ремесло"])
        self.add_skills["Строительство"] = int(
            randint(1000, 3100) * 0.001 * self.main_skills["Интеллект"] + 0.75 * self.main_skills["Физподготовка"])
        self.add_skills["Технические знания"] = int(
            randint(1000, 3100) * 0.001 * self.main_skills["Интеллект"] + 0.5 * self.add_skills["Общая эрудиция"])

    def _calculate_perception(self):
        self.add_skills["Скрытность"] = int(2.2 * self.main_skills["Восприятие"] + 1.5 * self.add_skills["Ловкость"])
        self.add_skills["Огнестрельное оружие"] = int(1.75 * self.main_skills["Восприятие"])
        self.add_skills["Луки и арбалеты"] = int(2 * self.main_skills["Восприятие"] + self.add_skills["Ловкость"])
        self.add_skills["Взлом"] = int(1.6 * self.main_skills["Восприятие"] + 2 * self.main_skills["Интеллект"])
        self.add_skills["Кража"] = int(2.2 * self.main_skills["Восприятие"] + 1.35 * self.main_skills["Интеллект"])
        self.add_skills["Метательное оружие"] = int(
            1.2 * self.main_skills["Восприятие"] + 1.7 * self.add_skills["Боевые искусства"])

    def _load_player(self, cursor: sqlite3.Cursor):
        cursor.execute("""
                        SELECT * FROM players where id = ?;
                        """, [self.id])
        player = cursor.fetchone()
        print(player)
        self.name = player[1]
        self.biography = player[2]
        self.money = player[3]

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
