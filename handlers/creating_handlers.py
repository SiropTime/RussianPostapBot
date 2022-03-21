from telegram import *

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ParseMode
from aiogram import types

from handlers.main_skills_handlers import MainSkillsForm


class Form(StatesGroup):
    name = State()
    biography = State()


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
        game.create_player(msg.from_user.id, data["name"], data["biography"], player)
    await state.finish()
    await msg.answer(MAIN_SKILLS_MSG_0, parse_mode=types.ParseMode.HTML)
    for i in range(len(MAIN_SKILLS_MSGS)):
        await msg.answer(MAIN_SKILLS_MSGS[i], parse_mode=types.ParseMode.MARKDOWN)

    await MainSkillsForm.physics.set()
    await msg.reply("Введите количество очков физической подготовки от 1 до 20:")


