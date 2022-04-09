from asyncio.base_futures import Error

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
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


# async def commands_list_menu(dis: Dispatcher):
#     await


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
    except TypeError:
        await msg.answer("На вас не зарегистрирован персонаж. Попробуйте создать нового!")
    try:
        await state.finish()
    except Error:
        print("Пользователь с id" + str(msg.from_user.id) + " не был в state")
    finally:
        await msg.answer("Введите /menu")

# Переменные для экспорта
__all__ = ["dp", "bot", "game", "player", "Form"]

if __name__ == "__main__":
    # Соединяем хэндлеры с основной программой
    from handlers import dp

    print(player.main_skills, player.add_skills)
    executor.start_polling(dp, skip_updates=True)


