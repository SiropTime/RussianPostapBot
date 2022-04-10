from datetime import datetime

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


class WriteJournal(StatesGroup):
    write = State()


@dp.message_handler(lambda msg: msg.from_user.id == ADMIN, state=Shout.shout)
async def processing_shout(msg: types.Message, state: FSMContext):
    for p in game.players.keys():
        try:
            await bot.send_message(p, emojize(":mega: ***Dungeon Master крикнул:*** " + msg.text,
                                              use_aliases=True),
                                   parse_mode=ParseMode.MARKDOWN)
        except ChatNotFound:
            logger.info("Игрок с id" + str(p) + " не имеет чата с ботом")
    await state.finish()


@dp.message_handler(lambda msg: msg.from_user.id == ADMIN, state=WriteJournal.write)
async def processing_journal_write(msg: types.Message, state: FSMContext):
    try:
        with open("journal.txt", "a") as f:
            f.write("[" + str(datetime.now()) + " | МАСТЕР]:\n" + msg.text + "\n[КОНЕЦ ЗАПИСИ]\n")
        await msg.answer("Успешно записано в журнал!")
        await state.finish()
    except OSError:
        logger.error("Ошибка при работе журнала")


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
        players_msg = game.prepare_players()
        for m in players_msg:
            await msg.answer(m, parse_mode=ParseMode.MARKDOWN)

    if msg.text == MASTER_BUTTONS[1]:
        with open("journal.txt", "r") as f:
            await msg.answer(emojize(":scroll: ***Журнал***:", use_aliases=True),
                             parse_mode=ParseMode.MARKDOWN)
            journal = f.read()\
                # .replace('\n', '').replace('\r', '')
            await msg.answer(journal)

    if msg.text == MASTER_BUTTONS[3]:
        await WriteJournal.write.set()
        await msg.answer(emojize(":scroll: ***Введите своё сообщение для журнала***:",
                                 use_aliases=True),
                         parse_mode=ParseMode.MARKDOWN)
