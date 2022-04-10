import asyncio
from asyncio.base_futures import Error

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor
from aiogram import types
from aiogram.utils.exceptions import ChatNotFound

from instruments.player import Player
from game import Game
from instruments.utility import TOKEN, START_MSG, logger

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
game = Game()
player = Player()
was_loaded = False


class Form(StatesGroup):
    name = State()
    biography = State()


@dp.message_handler(commands=['start'])
async def send_welcome(msg: types.Message):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Создание персонажа"),
        types.BotCommand("return", "Загрузка персонажа"),
        types.BotCommand("menu", "Вызов меню")
    ])
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


@dp.message_handler(commands=['return'], state="*")
async def return_player(msg: types.Message, state: FSMContext):
    player.id = msg.from_user.id
    try:
        player.load_player(game.cursor, game)
        was_loaded = True
    except TypeError:
        await msg.answer("На вас не зарегистрирован персонаж. Попробуйте создать нового!")
    try:
        await state.finish()
    except Error:
        logger.info("Пользователь с id" + str(msg.from_user.id) + " не был в state")
    finally:
        await msg.answer("Введите /menu")


async def on_startup(_):
    for p in game.players.keys():
        try:
            await bot.send_message(p, "Бот запущен заново, введите команду /return")
            await asyncio.sleep(1)
        except ChatNotFound:
            logger.info("Игрок с id" + str(p) + " не имеет чата с ботом")

# Переменные для экспорта
__all__ = ["dp", "bot", "game", "player", "Form", "was_loaded"]

if __name__ == "__main__":
    # Соединяем хэндлеры с основной программой
    from handlers import dp

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


