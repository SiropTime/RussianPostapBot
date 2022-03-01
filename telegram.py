from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiogram.utils.markdown as md

from game import *
from game_utils import *

TOKEN = "5218155011:AAF0GYeUQtMswyMXHhsULlrLHlnQrphEpA8"
ADMIN = 390919747

START_MSG = """
Здравствуй!
Этот бот предназначен для помощи в отыгрыше Словесной РПГ.
Сейчас нам нужно создать твоего персонажа, введи своё имя!
P.S. Если у тебя уже есть персонаж, введи команду /return
"""

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
player = Player()
game = Game()

kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(types.InlineKeyboardButton(text="Создать персонажа"))


class Form(StatesGroup):
    name = State()
    biography = State()


def check_player(id: int) -> bool:
    res = False
    for i in range(len(game.players)):
        if id == game.players[i].id:
            res = True
            return res
        else:
            res = False
    return res


@dp.message_handler(commands=['start'])
async def send_welcome(msg: types.Message):
    if not msg.from_user.id == ADMIN:
        await msg.answer("Здравствуй, Гейммастер")
    else:
        if not check_player(msg.from_user.id):
            await msg.answer(START_MSG)
            await Form.name.set()


@dp.message_handler(state=Form.name)
async def process_name(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = msg.text
    await Form.next()
    await msg.answer("Распиши кратко биографию своего героя.")


@dp.message_handler(state=Form.biography)
async def process_biography(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['biography'] = msg.text
        markup = types.ReplyKeyboardRemove()
        await msg.answer(md.text(md.text("Ваше имя: ", md.bold(data['name'])),
                                 md.text("Ваша биография: ", data['biography']),
                         md.text("Если вы совершили ошибку - введите команду /start ещё раз."),
                         md.text("Иначе введите команду /next для распределения навыков."), sep='\n'),
                         reply_markup=markup,
                         parse_mode=ParseMode.MARKDOWN)
    await state.finish()


@dp.message_handler(commands=['next'])
async def setup_main_skills(msg: types.Message):
    pass


@dp.message_handler(commands=['return'])
async def return_player(msg: types.Message):
    pass


if __name__ == "__main__":
    executor.start_polling(dp)
