from telegram import dp

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode
from emoji import emojize
from aiogram.dispatcher.filters.state import StatesGroup, State

from instruments.keyboards import main_menu_kb
from telegram import player


class Menu(StatesGroup):
    main = State()
    profile = State()


@dp.message_handler(commands=['menu'])
async def menu(msg: types.Message):
    await msg.answer("Меню", reply_markup=main_menu_kb)
    await Menu.main.set()


@dp.message_handler()
async def process_menu(msg: types.Message):
    if msg.text == emojize(":clipboard: Профиль", use_aliases=True):
        await msg.answer("Профиль", parse_mode=ParseMode.MARKDOWN)
        await msg.answer(player.prepare_profile()[0])
        await msg.answer(player.prepare_profile()[1])


@dp.message_handler(state=Menu.main)
async def main_menu(msg: types.Message, state: FSMContext):
    pass
