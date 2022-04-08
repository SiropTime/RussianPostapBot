from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor
from aiogram import types

from instruments.player import Player
from game import Game
from instruments.utility import TOKEN, START_MSG

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
game = Game()
player = Player()


class Form(StatesGroup):
    name = State()
    biography = State()


@dp.message_handler(commands=['start'])
async def send_welcome(msg: types.Message):
    await msg.answer(START_MSG)
    await Form.name.set()

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
    try:
        player.load_player(game.cursor)
    except TypeError:
        await msg.answer("На вас не зарегистрирован персонаж. Попробуйте создать нового!")

__all__ = ["dp", "bot", "game", "player"]

if __name__ == "__main__":
    from handlers import dp
    executor.start_polling(dp, skip_updates=True)
    player.load_player(game.cursor)
    print(player.main_skills, player.add_skills)
