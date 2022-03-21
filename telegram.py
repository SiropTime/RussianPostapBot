from contextlib import suppress

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import MessageNotModified

from keyboards import *
from emoji import emojize
import aiogram.utils.markdown as md

from game import *
from game_utils import *
from utility import *
from handlers.creating_handlers import *


bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
player = Player()
game = Game()
priority_skills = []


class Form(StatesGroup):
    name = State()
    biography = State()


class Menu(StatesGroup):
    main = State()
    profile = State()


def check_player(id: int) -> bool:
    res = False
    for i in range(len(game.players)):
        if id == game.players[i].id:
            res = True
            return res
        else:
            res = False
    return res


@dp.message_handler(commands=['return'])
async def return_player(msg: types.Message):
    player.id = msg.from_user.id
    player.load_player(game.cursor)


@dp.message_handler(commands=['menu'])
async def menu(msg: types.Message):
    await msg.answer("Меню", reply_markup=main_menu_kb)
    await Menu.main.set()


@dp.message_handler(commands=['start'])
async def send_welcome(msg: types.Message):
    # if not msg.from_user.id == ADMIN:
    #     await msg.answer("Здравствуй, Гейммастер")
    # else:
    await msg.answer(START_MSG)
    await Form.name.set()


@dp.message_handler()
async def process_menu(msg: types.Message):
    if msg.text == emojize(":clipboard: Профиль", use_aliases=True):
        await msg.answer("Профиль", parse_mode=ParseMode.MARKDOWN)
        await msg.answer(player.prepare_profile()[0])
        await msg.answer(player.prepare_profile()[1])


@dp.message_handler(state=Menu.main)
async def main_menu(msg: types.Message, state: FSMContext):
    pass


if __name__ == "__main__":
    executor.start_polling(dp)
    player.load_player(game.cursor)
    print(player.main_skills, player.add_skills)
