from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from emoji import emojize
import aiogram.utils.markdown as md

from game import *
from game_utils import *
from utility import *


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


class MainSkillsForm(StatesGroup):
    physics = State()
    intelligence = State()
    perception = State()
    charisma = State()


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
        await msg.answer(md.text(md.text("Ваше имя: ", md.bold(data['name'])),
                                 md.text("Ваша биография: ", data['biography']),
                                 md.text("Если вы совершили ошибку - введите команду /start ещё раз."),
                                 md.text("Иначе введите команду /next для распределения навыков."), sep='\n'),
                         parse_mode=ParseMode.MARKDOWN)
    await state.finish()


@dp.message_handler(commands=['next'])
async def setup_main_skills(msg: types.Message):
    await msg.answer(MAIN_SKILLS_MSG_0, parse_mode=types.ParseMode.HTML)
    for i in range(len(MAIN_SKILLS_MSGS)):
        await msg.answer(MAIN_SKILLS_MSGS[i], parse_mode=types.ParseMode.MARKDOWN)

    await MainSkillsForm.physics.set()
    await msg.reply("Введите количество очков физической подготовки от 1 до 20:")


@dp.message_handler(lambda msg: not msg.text.isdigit(), state=[MainSkillsForm.physics, MainSkillsForm.intelligence, MainSkillsForm.perception, MainSkillsForm.charisma])
async def process_skills_invalid(msg: types.Message):
    return await msg.reply("Напишите количество очков цифрами!")


@dp.message_handler(lambda msg: msg.text.isdigit(), state=MainSkillsForm.physics)
async def process_physics(msg: types.Message, state: FSMContext):
    await state.update_data(physics=int(msg.text))
    await MainSkillsForm.next()
    await msg.reply("Введите количество очков интеллекта от 1 до 20:")


@dp.message_handler(lambda msg: msg.text.isdigit(), state=MainSkillsForm.intelligence)
async def process_intelligence(msg: types.Message, state: FSMContext):
    await state.update_data(intelligence=int(msg.text))
    await MainSkillsForm.next()
    await msg.reply("Введите количество очков восприятия от 1 до 20:")


@dp.message_handler(lambda msg: msg.text.isdigit(), state=MainSkillsForm.perception)
async def process_perception(msg: types.Message, state: FSMContext):
    await state.update_data(perception=int(msg.text))
    await MainSkillsForm.next()
    await msg.reply("Введите количество очков харизмы от 1 до 20:")


@dp.message_handler(lambda msg: msg.text.isdigit(), state=MainSkillsForm.charisma)
async def process_charisma(msg: types.Message, state: FSMContext):
    await state.update_data(charisma=int(msg.text))
    async with state.proxy() as data:
        await msg.reply(md.text(data["physics"], data["intelligence"], data["perception"], data["charisma"]))

@dp.message_handler(commands=['return'])
async def return_player(msg: types.Message):
    pass


if __name__ == "__main__":
    executor.start_polling(dp)
