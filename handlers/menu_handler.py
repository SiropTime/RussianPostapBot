from contextlib import suppress
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ParseMode
from aiogram.utils.exceptions import MessageNotModified
import aiogram.utils.markdown as md
from emoji import emojize

from instruments.keyboards import main_menu_kb, profile_kb, btn_list, lvl_up_kb, return_kb
from instruments.utility import ADMIN, levels
from telegram import dp, game
from telegram import player, bot


class Menu(StatesGroup):
    main = State()
    profile = State()


class Profile(StatesGroup):
    status = State()
    main_skills = State()
    add_skills = State()
    inventory = State()


class LevelUp(StatesGroup):
    level_up = State()


class WriteJournal(StatesGroup):
    write = State()


class Bestiary(StatesGroup):
    bestiary = State()


@dp.message_handler(lambda msg: not msg.from_user.id == ADMIN, commands=['menu'])
async def menu(msg: types.Message):
    await msg.answer("Меню", reply_markup=main_menu_kb)


@dp.message_handler(lambda msg: not msg.from_user.id == ADMIN, commands=['level_up'])
async def level_up(msg: types.Message):
    if player.xp >= levels[player.level]:
        await msg.answer("Выберите навыки для повышения уровня", reply_markup=lvl_up_kb)
        player.level += 1
        await LevelUp.level_up.set()
    else:
        await msg.answer("Ваш уровень не поднялся!")


@dp.message_handler(lambda msg: not msg.from_user.id == ADMIN)
async def process_bestiary(msg: types.Message, state: FSMContext):
    if msg.text == emojize(":leftwards_arrow_with_hook: Обратно в меню", use_aliases=True):
        await state.finish()
        await msg.answer("Меню", reply_markup=main_menu_kb)
    else:
        for animal in game.animals:
            if animal.name == msg.text:
                an_msg = emojize(":paw_prints: ***" + animal.name + "***\n", use_aliases=True)
                an_msg += emojize("  :globe_with_meridians: ***Ареал обитания***: " + animal.area + "\n", use_aliases=True)
                an_msg += emojize("  :page_facing_up: ***Описание животного***: " + animal.description + "\n", use_aliases=True)
                await msg.answer(an_msg, parse_mode=ParseMode.MARKDOWN)
                break
        else:
            await msg.answer(emojize(":x: Такого животного ещё нет в бестиарии!", use_aliases=True))


level_up_skills = []


@dp.callback_query_handler(state=LevelUp.level_up)
async def process_level_up(callback_query: types.CallbackQuery, state: FSMContext):
    with suppress(MessageNotModified):
        if callback_query.data not in level_up_skills and not callback_query.data == "end":
            if len(level_up_skills) >= 3:
                await callback_query.answer(text="Вы уже выбрали 3 навыка! Уберите уже выбранные для изменения!",
                                            show_alert=True)
            else:
                btn_list[callback_query.data].text = "☑ " + btn_list[callback_query.data].text
                level_up_skills.append(callback_query.data)
        elif callback_query.data in level_up_skills:
            btn_list[callback_query.data].text = btn_list[callback_query.data].text[2:]
            level_up_skills.remove(callback_query.data)
        elif callback_query.data == "end":
            if len(level_up_skills) < 3:
                await callback_query.answer(text="Выберите 3 навыка!", show_alert=True)
            else:
                await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
                for skill, value in player.add_skills.items():
                    if skill in level_up_skills:
                        player.add_skills[skill] = int(value * 1.05)
                player.update_player(game.cursor, game.db)
                await state.finish()
                await bot.send_message(player.id, "Меню", reply_markup=main_menu_kb)


@dp.message_handler(lambda msg: not msg.from_user.id == ADMIN, state=WriteJournal.write)
async def processing_journal_write(msg: types.Message, state: FSMContext):
    with open("journal.txt", "a") as f:
        try:
            f.write("[" + str(datetime.now()) + " | " + player.name + "]:\n" + msg.text + "\n[КОНЕЦ ЗАПИСИ]\n\n")
            await msg.answer("Успешно записано в журнал!")
            await bot.send_message(ADMIN,
                                   emojize(
                                       ":triangular_flag_on_post: Добавлена новая запись в журнал от игрока с id: " +
                                       str(msg.from_user.id),
                                       use_aliases=True))
            await state.finish()
        except UnicodeEncodeError:
            await msg.answer("***Ошибка кодировки!***\nПопробуйте убрать спорные символы и смайлики!",
                             parse_mode=ParseMode.MARKDOWN)
            await msg.answer(emojize(":scroll: ***Введите своё сообщение для журнала***:",
                                     use_aliases=True),
                             parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(lambda msg: not msg.from_user.id == ADMIN)
async def process_menu(msg: types.Message):
    player.load_player(game.cursor, game)
    player_profile = player.prepare_profile()
    # Обработка главного меню
    if msg.text == emojize(":clipboard: Профиль", use_aliases=True):
        await msg.answer(emojize(":clipboard: ***Профиль***: " + player.name + "\n:mortar_board: ***Опыт/Уровень***: " +
                                 str(player.xp) + "/" + str(player.level) + "\n :moneybag: ***Деньги***:"
                                 + str(player.money)),
                         parse_mode=ParseMode.MARKDOWN,
                         reply_markup=profile_kb)

    if msg.text == emojize(":earth_asia: Местоположение", use_aliases=True):
        await msg.answer(emojize("Ваше местоположение: :earth_asia: ***" + player.location.name + "***",
                                 use_aliases=True),
                         parse_mode=ParseMode.MARKDOWN)
        await msg.answer(emojize(":scroll: ***Описание местоположения***: " + player.location.description,
                                 use_aliases=True),
                         parse_mode=ParseMode.MARKDOWN)
        await bot.send_location(msg.from_user.id, player.location.coordinates[0], player.location.coordinates[1])

    if msg.text == emojize(":arrow_up: Совершить действие", use_aliases=True):
        await msg.answer(emojize(msg.text, use_aliases=True))

    if msg.text == emojize(":email: Отправить текст отыгрыша", use_aliases=True):
        await WriteJournal.write.set()
        await msg.answer(emojize(":scroll: ***Введите своё сообщение для журнала***:",
                                 use_aliases=True),
                         parse_mode=ParseMode.MARKDOWN)

    if msg.text == emojize(":scroll: Журнал", use_aliases=True):
        with open("journal.txt", "r") as f:
            await msg.answer(emojize(":scroll: ***Журнал***:", use_aliases=True),
                             parse_mode=ParseMode.MARKDOWN)
            journal = f.read()
            await msg.answer(journal)

    if msg.text == emojize(":turtle: Бесстиарий", use_aliases=True):
        bes_msg = emojize(":turtle: ***Бесстиарий***\n\n", use_aliases=True)
        for animal in game.animals:
            bes_msg += emojize(":paw_prints: " + md.code(animal.name) + "\n")
        await msg.answer(bes_msg, parse_mode=ParseMode.MARKDOWN)
        await Bestiary.bestiary.set()
        await msg.answer(md.text("Чтобы узнать больше о животном, отправьте его имя",
                                 md.italic("(оно автоматически копируется при нажатии на него)!"),
                                 sep=" "), parse_mode=ParseMode.MARKDOWN, reply_markup=return_kb)

    # Обработка выхода из всех подменю
    if msg.text == emojize(":leftwards_arrow_with_hook: Обратно в меню", use_aliases=True):
        await msg.answer("Меню", reply_markup=main_menu_kb)

    # Обработка меню профиля
    if msg.text == emojize(":floppy_disk: Основные навыки", use_aliases=True):
        await msg.answer(player_profile[1], parse_mode=ParseMode.MARKDOWN)
    if msg.text == emojize(":game_die: Дополнительные навыки", use_aliases=True):
        await msg.answer(player_profile[2], parse_mode=ParseMode.MARKDOWN)
    if msg.text == emojize(":red_circle: Состояние", use_aliases=True):
        await msg.answer(player_profile[0], parse_mode=ParseMode.MARKDOWN)
    if msg.text == emojize(":handbag: Инвентарь", use_aliases=True):
        if len(player.inventory) == 0:
            await msg.answer(emojize(":handbag: ***Инвентарь***, а, стоп, здесь же __пусто__"),
                             parse_mode=ParseMode.MARKDOWN)
        else:
            await msg.answer(player_profile[3], parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(state=Menu.main)
async def main_menu(msg: types.Message, state: FSMContext):
    pass
