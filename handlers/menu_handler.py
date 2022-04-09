from telegram import dp, game

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode
from emoji import emojize
from aiogram.dispatcher.filters.state import StatesGroup, State

from instruments.keyboards import main_menu_kb, profile_kb
from telegram import player


class Menu(StatesGroup):
    main = State()
    profile = State()


class Profile(StatesGroup):
    status = State()
    main_skills = State()
    add_skills = State()
    inventory = State()


@dp.message_handler(commands=['menu'])
async def menu(msg: types.Message):
    await msg.answer("Меню", reply_markup=main_menu_kb)
    # await Menu.main.set()


@dp.message_handler()
async def process_menu(msg: types.Message):
    player.id = int(msg.from_user.id)
    player.load_player(game.cursor)
    player_profile = player.prepare_profile()
    if msg.text == emojize(":clipboard: Профиль", use_aliases=True):
        await msg.answer(emojize(":clipboard: ***Профиль***: " + player.name), parse_mode=ParseMode.MARKDOWN,
                         reply_markup=profile_kb)
    if msg.text == emojize(":leftwards_arrow_with_hook: Обратно в меню", use_aliases=True):
        await msg.answer("Меню", reply_markup=main_menu_kb)
    if msg.text == emojize(":floppy_disk: Основные навыки", use_aliases=True):
        await msg.answer(player_profile[1], parse_mode=ParseMode.MARKDOWN)
    if msg.text == emojize(":game_die: Дополнительные навыки", use_aliases=True):
        await msg.answer(player_profile[2], parse_mode=ParseMode.MARKDOWN)
    if msg.text == emojize(":red_circle: Состояние", use_aliases=True):
        await msg.answer(player_profile[0], parse_mode=ParseMode.MARKDOWN)
    if msg.text == emojize(":handbag: Инвентарь", use_aliases=True):
        await msg.answer(player_profile[3], parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(state=Menu.main)
async def main_menu(msg: types.Message, state: FSMContext):
    pass
