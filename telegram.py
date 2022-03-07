from contextlib import suppress

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import MessageNotModified

from keyboards import *
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
priority_skills = []

class Form(StatesGroup):
    name = State()
    biography = State()


class MainSkillsForm(StatesGroup):
    physics = State()
    intelligence = State()
    perception = State()
    charisma = State()


class AddSkillsForm(StatesGroup):
    choosing = State()


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
    # if not msg.from_user.id == ADMIN:
    #     await msg.answer("Здравствуй, Гейммастер")
    # else:
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
        game.create_player(msg.from_user.id, data["name"], data["biography"], player)
    await state.finish()
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
        player.main_skills["Физподготовка"] = data["physics"]
        player.main_skills["Интеллект"] = data["intelligence"]
        player.main_skills["Восприятие"] = data["perception"]
        player.main_skills["Харизма"] = data["charisma"]
        player.setup_main_skills(game.cursor, game.db)
        await msg.reply(md.text(md.bold(emojize("Ваши основные навыки:")),
                                md.text(emojize(":muscle: ***Физподготовка***:"), data["physics"]),
                                md.text(emojize(":brain: ***Интеллект***:"), data["intelligence"]),
                                md.text(emojize(":eyes: ***Восприятие***:"), data["perception"]),
                                md.text(emojize(":bust_in_silhouette: ***Харизма***:"), data["charisma"]),
                                sep="\n"), parse_mode=types.ParseMode.MARKDOWN)
        await msg.reply(md.text("Отлично! Теперь распределим твои дополнительные навыки, умения.",
                                "Учти, что ты можешь выбрать ***всего 5 навыков***, которые",
                                "будут лучше прокачаны изначально и будут развивать лучше",
                                "в будущеи.", sep=" "), reply_markup=add_skills_kb, parse_mode=types.ParseMode.MARKDOWN)
        await state.finish()


@dp.callback_query_handler()
async def process_add_skills(callback_query: types.CallbackQuery):
    with suppress(MessageNotModified):
        if callback_query.data not in priority_skills and not callback_query.data == "end":
            if len(priority_skills) >= 5:
                await callback_query.answer(text="Вы уже выбрали 5 навыков! Уберите уже выбранные для изменения!", show_alert=True)
            else:
                button_list[callback_query.data].text += " ☑"
                priority_skills.append(callback_query.data)
        elif callback_query.data in priority_skills:
            button_list[callback_query.data].text = button_list[callback_query.data].text[:-2]
            priority_skills.remove(callback_query.data)
        elif callback_query.data == "end":
            if len(priority_skills) < 5:
                await callback_query.answer(text="Выберите 5 навыков!", show_alert=True)
            else:
                await callback_query.message.edit_text("Успешно!")
                player.priority_skills = priority_skills
    print(priority_skills)

    await callback_query.message.edit_reply_markup(reply_markup=add_skills_kb)
    await callback_query.answer()


@dp.message_handler(commands=['return'])
async def return_player(msg: types.Message):
    pass


if __name__ == "__main__":
    executor.start_polling(dp)
