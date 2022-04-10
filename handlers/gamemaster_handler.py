import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ParseMode
from aiogram.utils.exceptions import ChatNotFound
from emoji import emojize

from instruments.keyboards import gamemaster_kb
from instruments.utility import ADMIN, MASTER_BUTTONS
from telegram import dp, game, bot, logger


class Shout(StatesGroup):
    shout = State()


@dp.message_handler(lambda msg: msg.from_user.id == ADMIN, state=Shout.shout)
async def processing_shout(msg: types.Message, state=FSMContext):
    for p in game.players.keys():
        try:
            await bot.send_message(p, emojize(":mega: ***Dungeon Master крикнул:*** " + msg.text,
                                              use_aliases=True),
                                   parse_mode=ParseMode.MARKDOWN)
        except ChatNotFound:
            logger.info("Игрок с id" + str(p) + " не имеет чата с ботом")
    await state.finish()


@dp.message_handler(lambda msg: msg.from_user.id == ADMIN)
async def admin_console_processing(msg: types.Message):
    await msg.answer(emojize(":mortar_board: ***Меню гейм мастера***", use_aliases=True),
                     parse_mode=ParseMode.MARKDOWN, reply_markup=gamemaster_kb)
    if '!к' in msg.text:
        command = list(map(str, msg.text[2:].split()))
        logger.info(command)

    if msg.text == MASTER_BUTTONS[2]:
        await Shout.shout.set()
        await msg.answer(emojize(":mega: Введите своё ***сообщение*** для игроков:",
                                 use_aliases=True),
                         parse_mode=ParseMode.MARKDOWN)

    if msg.text == MASTER_BUTTONS[0]:
        pass
