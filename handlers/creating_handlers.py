from emoji import emojize
from time import sleep

from telegram import dp

from aiogram.dispatcher import FSMContext
from aiogram.utils import markdown as md
from aiogram.types import ParseMode
from aiogram import types

from handlers.main_skills_handlers import MainSkillsForm
from instruments.utility import MAIN_SKILLS_MSG_0, MAIN_SKILLS_MSGS
from telegram import game, player, Form


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
                                 sep='\n'),
                         parse_mode=ParseMode.MARKDOWN)
        game.create_player(msg.from_user.id, data["name"], data["biography"], player)
    await state.finish()
    await msg.answer(MAIN_SKILLS_MSG_0, parse_mode=types.ParseMode.HTML)
    for i in range(len(MAIN_SKILLS_MSGS)):
        sleep(2)
        await msg.answer(MAIN_SKILLS_MSGS[i], parse_mode=types.ParseMode.MARKDOWN)

    await MainSkillsForm.physics.set()
    await msg.answer(emojize("Введите количество очков :muscle: ***физической подготовки*** от 1 до 20:",
                             use_aliases=True),
                     parse_mode=ParseMode.MARKDOWN)


