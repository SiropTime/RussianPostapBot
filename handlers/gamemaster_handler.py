from asyncio import sleep
from datetime import datetime
from typing import List

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ParseMode
from aiogram.utils.exceptions import ChatNotFound
from emoji import emojize

from instruments.game_utils import Location, Animal, Item, check_skill
from instruments.keyboards import gamemaster_kb
from instruments.utility import ADMIN, MASTER_BUTTONS, logger, levels
from telegram import dp, game, bot


class Shout(StatesGroup):
    shout = State()


class WriteJournal(StatesGroup):
    write = State()


@dp.message_handler(lambda msg: msg.from_user.id == ADMIN, state=Shout.shout)
async def processing_shout(msg: types.Message, state: FSMContext):
    for p in game.players.keys():
        try:
            await bot.send_message(p, emojize(":mega: ***Dungeon Master крикнул:*** " + msg.text,
                                              use_aliases=True),
                                   parse_mode=ParseMode.MARKDOWN)
        except ChatNotFound:
            logger.info("Игрок с id" + str(p) + " не имеет чата с ботом")
    await state.finish()


@dp.message_handler(lambda msg: msg.from_user.id == ADMIN, state=WriteJournal.write)
async def processing_journal_write(msg: types.Message, state: FSMContext):
    try:
        with open("journal.txt", "a") as f:
            try:
                f.write("[" + str(datetime.now()) + " | МАСТЕР]:\n" + msg.text + "\n[КОНЕЦ ЗАПИСИ]\n\n")
                await msg.answer("Успешно записано в журнал!")
                await state.finish()
            except UnicodeEncodeError:
                await msg.answer("***Ошибка кодировки!***\nПопробуйте убрать спорные символы и смайлики!",
                                 parse_mode=ParseMode.MARKDOWN)
                await msg.answer(emojize(":scroll: ***Введите своё сообщение для журнала***:",
                                         use_aliases=True),
                                 parse_mode=ParseMode.MARKDOWN)
    except OSError:
        logger.error("Ошибка при работе c журналом")


def process_string(s: str):
    res = s[0]
    for letter in s[1:]:
        if letter == letter.upper():
            res += " " + letter
        else:
            res += letter
    return res


async def admin_console_processing(command: List[str]):
    if command[0] == 'добавить':
        if command[1] == 'локация':
            location = Location()
            _loc = command[2][1:-2].split(sep=",")
            location.name = _loc[0]
            try:
                location.coordinates = (float(_loc[1]), float(_loc[2]))
            except ValueError:
                await bot.send_message(ADMIN, "Координаты имеют не вещественный тип! Проверьте, точно ли это числа!")
            command = command[3:]
            location.description = " ".join(command)
            game.locations.append(location)
            game.update_locations()
            await bot.send_message(ADMIN, "***Успешно!***", parse_mode=ParseMode.MARKDOWN)

        elif command[1] == 'животное':
            animal = Animal()
            name = process_string(command[2])
            animal.name = name
            animal.area = process_string(command[3])
            command = command[4:]
            animal.description = " ".join(command)
            logger.info(" ".join((animal.name, animal.area, animal.description)))
            game.animals.append(animal)
            game.update_animals()
            await bot.send_message(ADMIN, "***Успешно!***", parse_mode=ParseMode.MARKDOWN)

        elif command[1] == 'предмет':
            item = Item()
            try:
                id = int(command[2])
                item.quantity = int(command[4])
                item.name = process_string(command[3])
                item.description = " ".join(command[5:])
                game.players[id].add_item_to_inventory(game.cursor, game.db, item)
                await bot.send_message(ADMIN, "***Успешно!***", parse_mode=ParseMode.MARKDOWN)
            except ValueError:
                await bot.send_message(ADMIN, "ID и количество предметов должно быть числами!")

        elif command[1] == 'опыт':
            try:
                id = int(command[2])
                game.players[id].xp += int(command[3])
                await bot.send_message(id, "Вы получили ***" + command[3] + " опыта!***", parse_mode=ParseMode.MARKDOWN)
                if game.players[id].xp >= levels[game.players[id].level]:
                    await bot.send_message(id, "Вам доступно повышение уровня! Введите команду /level_up, чтобы "
                                               "повысить навыки!")
                game.players[id].update_player(game.cursor, game.db)
                await bot.send_message(ADMIN, "***Успешно!***", parse_mode=ParseMode.MARKDOWN)
            except ValueError:
                await bot.send_message(ADMIN, "ID и количество опыта должны быть числами!")

        elif command[1] == 'деньги':
            try:
                id = int(command[2])
                game.players[id].money += int(command[3])
                game.players[id].update_player(game.cursor, game.db)
                await bot.send_message(ADMIN, "***Успешно!***", parse_mode=ParseMode.MARKDOWN)
            except ValueError:
                await bot.send_message(ADMIN, "ID и количество денег должны быть числами!")

        else:
            await bot.send_message(ADMIN, f"***Неверный синтаксис***, такого сочетания с '{command[0]}' нет!",
                                   parse_mode=ParseMode.MARKDOWN)
    elif command[0] == 'проверить':
        if command[1] == 'осн_навык':
            id = int(command[2])
            skill = process_string(command[3])
            bonuses = list(map(int, command[4][1:-1].split(sep=",")))
            flag = True
            try:
                description = " ".join(command[5:])
            except IndexError:
                logger.info("Нет описания события!")
                description = ""
            logger.info(str(id) + skill + str(bonuses))
            try:
                skill_value = game.players[id].main_skills[skill]
            except KeyError:
                flag = False
                skill_value = 0
                await bot.send_message(ADMIN, f"***Такого навыка {skill} не существует!***"
                                              f"\nПроверьте на наличие опечаток или посмотрите список основных навыков",
                                       parse_mode=ParseMode.MARKDOWN)

            await bot.send_message(id, "Вызвана проверка основного навыка - ***" + skill + "***."
                                                                                           "\n***Описание события:***",
                                   parse_mode=ParseMode.MARKDOWN)
            if not description == "":
                await bot.send_message(id, description)
            else:
                await bot.send_message(id, "Описание забрали рейдеры пустоши!")

            if flag:
                is_successful = check_skill(skill_value, bonuses, (-1, 21))

                await sleep(2)
                if is_successful:
                    await bot.send_message(ADMIN, emojize(":white_check_mark: ***Успешно!***", use_aliases=True),
                                           parse_mode=ParseMode.MARKDOWN)
                    await bot.send_message(id, emojize(":white_check_mark: ***Успешно!***", use_aliases=True),
                                           parse_mode=ParseMode.MARKDOWN)
                else:
                    await bot.send_message(ADMIN, emojize(":x: ***Провал!***", use_aliases=True),
                                           parse_mode=ParseMode.MARKDOWN)
                    await bot.send_message(id, emojize(":x: ***Провал!***", use_aliases=True),
                                           parse_mode=ParseMode.MARKDOWN)

        elif command[1] == 'доп_навык':
            id = int(command[2])
            skill = process_string(command[3])
            bonuses = list(map(int, command[4][1:-1].split(sep=",")))
            flag = True
            try:
                description = " ".join(command[5:])
            except IndexError:
                logger.info("Нет описания события!")
                description = ""
            logger.info(str(id) + skill + str(bonuses))
            try:
                skill_value = game.players[id].add_skills[skill]
            except KeyError:
                flag = False
                skill_value = 0
                await bot.send_message(ADMIN, f"***Такого навыка {skill} не существует!***"
                                              f"\nПроверьте на наличие опечаток или посмотрите список"
                                              f"дополнительных навыков",
                                       parse_mode=ParseMode.MARKDOWN)

            await bot.send_message(id, "Вызвана проверка дополнительного навыка - ***" + skill + "***."
                                                                                                 "\n***Описание "
                                                                                                 "события:***",
                                   parse_mode=ParseMode.MARKDOWN)
            if not description == "":
                await bot.send_message(id, description)
            else:
                await bot.send_message(id, "Описание забрали рейдеры пустоши!")

            if flag:
                is_successful = check_skill(skill_value, bonuses, (-5, 105))

                await sleep(2)
                if is_successful:
                    await bot.send_message(ADMIN, emojize(":white_check_mark: ***Успешно!***", use_aliases=True),
                                           parse_mode=ParseMode.MARKDOWN)
                    await bot.send_message(id, emojize(":white_check_mark: ***Успешно!***", use_aliases=True),
                                           parse_mode=ParseMode.MARKDOWN)
                else:
                    await bot.send_message(ADMIN, emojize(":x: ***Провал!***", use_aliases=True),
                                           parse_mode=ParseMode.MARKDOWN)
                    await bot.send_message(id, emojize(":x: ***Провал!***", use_aliases=True),
                                           parse_mode=ParseMode.MARKDOWN)
        else:
            await bot.send_message(ADMIN, f"***Неверный синтаксис***, такого сочетания с '{command[0]}' нет!",
                                   parse_mode=ParseMode.MARKDOWN)
    elif command[0] == 'изменить':
        if command[1] == "статус":
            id = int(command[2])
            status = process_string(command[3])

            # Проверяем целое число ли дано
            try:
                num = int(command[4])
                # Проверяем на наличие статуса в списке
                try:
                    val = game.players[id].status[status]
                    if val + num <= 0:
                        await bot.send_message(ADMIN,
                                               f"Значение состояния части тела ***{status}*** игрока {id} меньше нуля.\n"
                                               f"Персонаж теряет эту часть тела.\n ***Учтите это!***",
                                               parse_mode=ParseMode.MARKDOWN)
                    game.players[id].status[status] += num
                    game.players[id].update_player()
                except KeyError:
                    await bot.send_message(ADMIN, "Такого статуса нет! Проверьте список состояний игрока!")

            except ValueError:
                await bot.send_message(ADMIN, "Значение должно быть числом!")

        elif command[1] == "инвентарь":
            item = process_string(command[3])
            id = int(command[2])
            quantity = int(command[4])
            if quantity <= 0:
                game.players[id].delete_item(item, game.cursor, game.db)
            else:
                game.players[id].update_item(item, quantity, game.cursor, game.db)
            await bot.send_message(ADMIN, emojize(":white_check_mark: ***Успешно!***", use_aliases=True),
                                   parse_mode=ParseMode.MARKDOWN)


        else:
            await bot.send_message(ADMIN, f"***Неверный синтаксис***, такого сочетания с '{command[0]}' нет!",
                                   parse_mode=ParseMode.MARKDOWN)
    else:
        await bot.send_message(ADMIN, f"***Неверный синтаксис***, такой команды как f{command[0]} нет!",
                               parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(lambda msg: msg.from_user.id == ADMIN, commands=['menu'])
async def process_admin_menu(msg: types.Message):
    await msg.answer(emojize(":mortar_board: ***Меню гейм мастера***", use_aliases=True),
                     parse_mode=ParseMode.MARKDOWN, reply_markup=gamemaster_kb)


@dp.message_handler(lambda msg: msg.from_user.id == ADMIN)
async def admin_menu_processing(msg: types.Message):
    if '!' in msg.text:
        if '!к' in msg.text:
            command = list(map(str, msg.text[2:].split()))
            logger.info(command)
            await admin_console_processing(command)
        else:
            await msg.answer("Команда введена неверно. Наверное, вы забыли ```!к```",
                             parse_mode=ParseMode.MARKDOWN)

    if msg.text == MASTER_BUTTONS[2]:
        await Shout.shout.set()
        await msg.answer(emojize(":mega: Введите своё ***сообщение*** для игроков:",
                                 use_aliases=True),
                         parse_mode=ParseMode.MARKDOWN)

    if msg.text == MASTER_BUTTONS[0]:
        players_msg = game.prepare_players()
        for m in players_msg:
            await msg.answer(m, parse_mode=ParseMode.MARKDOWN)

    if msg.text == MASTER_BUTTONS[1]:
        with open("journal.txt", "r") as f:
            await msg.answer(emojize(":scroll: ***Журнал***:", use_aliases=True),
                             parse_mode=ParseMode.MARKDOWN)
            journal = f.read()
            await msg.answer(journal)

    if msg.text == MASTER_BUTTONS[3]:
        await WriteJournal.write.set()
        await msg.answer(emojize(":scroll: ***Введите своё сообщение для журнала***:",
                                 use_aliases=True),
                         parse_mode=ParseMode.MARKDOWN)
