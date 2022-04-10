import sqlite3
from random import randint

from emoji import emojize
from aiogram.utils import markdown as md

from instruments.game_utils import Item
from instruments.utility import logger

__all__ = ["Player"]


class Player:
    def __init__(self):
        self.id = 0
        self.name = ""
        self.biography = ""
        self.inventory = []
        self.money = 0
        self.level = 0
        self.location = None
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

    def prepare_profile(self):
        """
        Подготовка всех данных для вывода профиля
        :return: Массив из четырёх подготовленных к выводу сообщений: Статус, Осн. Навыки, Доп. Навыки, Инвентарь
        """
        status_msg = emojize(":red_circle: ***Состояние персонажа***\n\n")
        for k, v in self.status.items():
            status_msg += emojize("   :small_red_triangle: ***" + k + "***: " + str(v) + "\n", use_aliases=True)
        main_chars_msg = md.text(
            emojize(":floppy_disk: ***Основные характеристики***:\n",
                    use_aliases=True),
            emojize("   :muscle: Физподготовка: " + str(self.main_skills["Физподготовка"]),
                    use_aliases=True),
            emojize("   :brain: Интеллект: " + str(self.main_skills["Интеллект"]),
                    use_aliases=True),
            emojize("   :eyes: Восприятие: " + str(self.main_skills["Восприятие"]),
                    use_aliases=True),
            emojize("   :bust_in_silhouette: Харизма: " + str(self.main_skills["Харизма"]),
                    use_aliases=True),
            sep="\n")
        add_chars_msg = emojize(":game_die: ***Дополнительные характеристики***\n\n", use_aliases=True)
        for k, v in self.add_skills.items():
            add_chars_msg += emojize("   :small_orange_diamond: ***" + k + "***: " + str(v) + "\n")

        inventory_msg = emojize(":handbag: ***Инвентарь***\n", use_aliases=True)
        for i in range(len(self.inventory)):
            item = self.inventory[i]
            item_msg = emojize(":white_small_square: ***" + item.name + "***. ", use_aliases=True)
            if item.quantity != 1:
                item_msg += "***Кол-во***: " + str(item.quantity) + "."
            inventory_msg += item_msg + "\n"
        return [status_msg, main_chars_msg, add_chars_msg, inventory_msg]

    # Добавление предмета в базу данных инвентаря
    def add_item_to_inventory(self, cursor: sqlite3.Cursor, item: Item):
        self.inventory.append(item)
        cursor.execute("""
                        INSERT INTO inventory (player_id, item, quantity, description, is_usable) VALUES
                        (?, ?, ?, ?, ?)
                        """, (self.id, item.name, item.quantity, item.description, item.is_usable))

    # Создаём персонажа и загружаем его в бд.
    #
    def create_player(self, cursor: sqlite3.Cursor, connection: sqlite3.Connection):
        cursor.execute("""
                       INSERT INTO players (id, name, biography) VALUES (?, ?, ?);
                       """,
                       (self.id, self.name, self.biography))
        cursor.execute("""
                       INSERT INTO status VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                       """, (self.id, 100, 100, 100, 100, 100, 100, 100, 100, 600, 4600))
        cursor.execute("""
                       DELETE FROM inventory WHERE player_id = ?;
                       """, [self.id])
        logger.info(self.id, self.name, self.biography)
        logger.info("Успешно загружен id" + str(self.id))
        connection.commit()

    # Обновляем данные об игроке в БД
    def update_player(self, cursor: sqlite3.Cursor, connection: sqlite3.Connection):
        self._update_player(cursor)
        self._update_status(cursor)
        self._update_main_skills(cursor)
        self._update_add_skills(cursor)
        logger.info("Обновление игрока с id" + str(self.id) + " завершено успешно")
        connection.commit()

    # Отправляем основные навыки в базу данных
    def setup_main_skills(self, cursor: sqlite3.Cursor, connection: sqlite3.Connection):
        temp = [self.id]
        for i in self.main_skills.values():
            temp.append(i)
        logger.info(temp)
        cursor.execute("""
                       INSERT INTO main_skills (player_id, physical, intelligence, perception, charisma)
                       VALUES (?, ?, ?, ?, ?);
                       """, tuple(temp))
        connection.commit()

    def load_player(self, cursor: sqlite3.Cursor, game):
        """
        Метод загрузки всех данных персонажа из базы данных. Реализует это через приватные методы
        :param game: Объект Game, необходим для проверки локаций
        :param cursor: Курсор, связанный с нашей базой данных
        :return: None
        """
        self._load_player(cursor, game)
        self._load_status(cursor)
        self._load_inventory(cursor)
        self._load_main_skills(cursor)
        self._load_add_skills(cursor)
        logger.info("Успешно завершена загрузка персонажа с id:" + str(self.id))

    # Удаление предмета из инвентаря
    def delete_item(self, item: Item):
        pass

    # Изменение количества предметов в инвентаре
    def update_quantity_of_item(self, item: Item, quantity: int):
        pass

    def calculate_skills(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
        """
        Расчёт дополнительных навыков на базе основных навыков
        :param cursor: Курсор, подключённый к БД
        :param conn: Объект БД SQLite
        :return: None
        """
        self._calculate_physics()
        self._calculate_intelligence()
        self._calculate_perception()
        self.add_skills["Психологическая устойчивость"] = int(
            0.9 * self.add_skills["Устойчивость"] + 2 * self.main_skills["Интеллект"])
        for skill, value in self.add_skills.items():
            self.add_skills[skill] = int(value * 0.6)
        for skill in self.priority_skills:
            self.add_skills[skill] = int(self.add_skills[skill] * 1.25)

        cursor.execute("""
                        INSERT INTO add_skill VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                        ?, ?, ?, ?, ?, ?, ?, ?);
                        """, tuple([self.id] + [s for s in self.add_skills.values()]))
        conn.commit()

    # Приватные методы
    #
    #

    # Расчёт навыков, преимущественно связанных с Физподготовкой
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
            self.add_skills[k] = int(
                (randint(10, 20) * 0.1) * self.main_skills["Физподготовка"] + 0.5 * self.add_skills["Боевые искусства"])

    # Расчёт навыков, преимущественно связанных с интеллектом
    def _calculate_intelligence(self):
        self.add_skills["Взрывчатка"] = int(1.25 * self.main_skills["Интеллект"])
        self.add_skills["Ловушки"] = int(1.25 * self.main_skills["Интеллект"])
        self.add_skills["Красноречие"] = int(1.8 * self.main_skills["Интеллект"] + 2.15 * self.main_skills["Харизма"])
        self.add_skills["Общая эрудиция"] = int(4 * self.main_skills["Интеллект"])
        self.add_skills["Медицина"] = int(1.5 * self.main_skills["Интеллект"] + 0.6 * self.add_skills["Общая эрудиция"])
        self.add_skills["Ремесло"] = int(randint(1000, 3100) * 0.001 * self.main_skills["Интеллект"])
        self.add_skills["Кузнечество"] = int(
            randint(1000, 3100) * 0.001 * self.main_skills["Интеллект"] + 0.5 * self.add_skills["Ремесло"])
        self.add_skills["Кожевничество"] = int(
            randint(1000, 3100) * 0.001 * self.main_skills["Интеллект"] + 0.5 * self.add_skills["Ремесло"])
        self.add_skills["Строительство"] = int(
            randint(1000, 3100) * 0.001 * self.main_skills["Интеллект"] + 0.75 * self.main_skills["Физподготовка"])
        self.add_skills["Технические знания"] = int(
            randint(1000, 3100) * 0.001 * self.main_skills["Интеллект"] + 0.5 * self.add_skills["Общая эрудиция"])

    # Расчёт навыков, преимущественно связанных с восприятием
    def _calculate_perception(self):
        self.add_skills["Скрытность"] = int(2.2 * self.main_skills["Восприятие"] + 1.5 * self.add_skills["Ловкость"])
        self.add_skills["Огнестрельное оружие"] = int(1.75 * self.main_skills["Восприятие"])
        self.add_skills["Луки и арбалеты"] = int(2 * self.main_skills["Восприятие"] + self.add_skills["Ловкость"])
        self.add_skills["Взлом"] = int(1.6 * self.main_skills["Восприятие"] + 2 * self.main_skills["Интеллект"])
        self.add_skills["Кража"] = int(2.2 * self.main_skills["Восприятие"] + 1.35 * self.main_skills["Интеллект"])
        self.add_skills["Метательное оружие"] = int(
            1.2 * self.main_skills["Восприятие"] + 1.7 * self.add_skills["Боевые искусства"])

    # Методы для загрузки данных из БД
    def _load_player(self, cursor: sqlite3.Cursor, game):
        cursor.execute("""
                        SELECT * FROM players where id = ?;
                        """, [self.id])
        player = cursor.fetchone()
        self.name = player[1]
        self.biography = player[2]
        self.money = player[3]
        self._get_location(player[4], game)
        self.level = player[5]

    def _update_player(self, cursor: sqlite3.Cursor):
        cursor.execute("""
                               INSERT INTO players (id, name, biography, money, location, level) VALUES (?, ?, ?, ?, ?, ?);
                               """,
                       (self.id, self.name, self.biography, self.money, self.location.name, self.level))

    # Проверка локации среди всех возможных в игре
    def _get_location(self, loc_name: str, game):
        for loc in game.locations:
            if loc_name == loc.name:
                self.location = loc
                break
        else:
            logger.exception("У персонажа с id" + str(self.id) + " не указана локация, установлена стандартная")
            self.location = game.locations[3]  # Село Архангельское
            game.cursor.execute("""
                                UPDATE players SET location = ? WHERE id = ?;
                                """, (self.location.name, self.id))
            game.db.commit()

    # Загрузка состояния персонажа из БД
    def _load_status(self, cursor: sqlite3.Cursor):
        cursor.execute("""
                               SELECT * FROM status where player_id = ?;
                               """, [self.id])
        status = cursor.fetchone()

        i = 1
        for stat in self.status.keys():
            self.status[stat] = status[i]
            i += 1

    def _update_status(self, cursor: sqlite3.Cursor):
        cursor.execute("""
                        INSERT INTO status VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                       """, [self.id] + [x for x in self.status.values()])

    # Загрузка инвентаря из БД
    def _load_inventory(self, cursor: sqlite3.Cursor):
        self.inventory = []
        cursor.execute("""
                                       SELECT * FROM inventory where player_id = ?;
                                       """, [self.id])
        inventory = cursor.fetchall()

        for i in range(len(inventory)):
            item = Item()
            item.name = inventory[i][1]
            item.quantity = inventory[i][2]
            item.description = inventory[i][3]
            item.is_usable = inventory[i][4]
            self.inventory.append(item)

    # Загрузка основных навыков из БД
    def _load_main_skills(self, cursor: sqlite3.Cursor):
        cursor.execute("""
                                               SELECT * FROM main_skills where player_id = ?;
                                               """, [self.id])
        main_skills = cursor.fetchone()

        i = 1
        for skill in self.main_skills.keys():
            self.main_skills[skill] = main_skills[i]
            i += 1

    def _update_main_skills(self, cursor: sqlite3.Cursor):
        cursor.execute("""
                       INSERT INTO main_skills VALUES (?, ?, ?, ?, ?);
                       """, [self.id] + [x for x in self.main_skills.values()])

    # Загрузка дополнительных навыков БД
    def _load_add_skills(self, cursor: sqlite3.Cursor):
        cursor.execute("""
                                                       SELECT * FROM add_skill where player_id = ?;
                                                       """, [self.id])
        add_skills = cursor.fetchone()

        i = 1
        for skill in self.add_skills.keys():
            self.add_skills[skill] = add_skills[i]
            i += 1

    def _update_add_skills(self, cursor: sqlite3.Cursor):
        cursor.execute("""
                        INSERT INTO add_skill VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                        ?, ?, ?, ?, ?, ?, ?, ?);
                       """, [self.id] + [x for x in self.add_skills.values()])
