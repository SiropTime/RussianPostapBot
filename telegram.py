from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from handlers.creating_handlers import *
from instruments.player import Player, Game
from instruments.utility import START_MSG, TOKEN

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
player = Player()
game = Game()
priority_skills = []


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


@dp.message_handler(commands=['start'])
async def send_welcome(msg: types.Message):
    await msg.answer(START_MSG)
    await Form.name.set()


if __name__ == "__main__":
    executor.start_polling(dp)
    player.load_player(game.cursor)
    print(player.main_skills, player.add_skills)
