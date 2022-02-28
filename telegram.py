from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from game import *
from game_utils import *

TOKEN = "5218155011:AAF0GYeUQtMswyMXHhsULlrLHlnQrphEpA8"
ADMIN = 390919747
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
player = Player()
game = Game()

kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(types.InlineKeyboardButton(text="Создать персонажа"))


def check_player(id: int) -> bool:
    res = False
    for i in range(len(game.players)):
        if id == game.players[i].id:
            res = True
            return res
        else:
            res = False


@dp.message_handler(commands=['start'])
async def send_welcome(msg: types.Message):
    if check_player(msg.from_user.id):
        await msg.answer("""
                        Здравствуй!
                        Этот бот предназначен для помощи в отыгрыше Словесной РПГ.
                        Сейчас нам нужно создать твоего персонажа, введи своё имя!
                        P.S. Если у тебя уже есть персонаж, введи команду /return
                        """)
    player.id = msg.from_user.id

@dp.message_handler(commands=['return'])
async def return_player(msg: types.Message):
    pass


if __name__ == "__main__":
    executor.start_polling(dp)
