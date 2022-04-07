from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.dispatcher.filters.state import State
from emoji import emojize
from aiogram.utils import markdown as md

from handlers.add_skills_handlers import AddSkillsForm
from instruments.keyboards import add_skills_kb
from telegram import dp, player, game


class MainSkillsForm(StatesGroup):
    physics = State()
    intelligence = State()
    perception = State()
    charisma = State()


@dp.message_handler(lambda msg: not msg.text.isdigit(),
                    state=[MainSkillsForm.physics, MainSkillsForm.intelligence, MainSkillsForm.perception,
                           MainSkillsForm.charisma])
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
                                md.text(emojize(":muscle: ***Физподготовка***:", use_aliases=True),
                                        data["physics"]),
                                md.text(emojize(":brain: ***Интеллект***:", use_aliases=True),
                                        data["intelligence"]),
                                md.text(emojize(":eyes: ***Восприятие***:", use_aliases=True), data["perception"]),
                                md.text(emojize(":bust_in_silhouette: ***Харизма***:", use_aliases=True),
                                        data["charisma"]),
                                sep="\n"), parse_mode=types.ParseMode.MARKDOWN)
        await msg.reply(md.text("Отлично! Теперь распределим твои дополнительные навыки, умения.",
                                "Учти, что ты можешь выбрать ***всего 5 навыков***, которые",
                                "будут лучше прокачаны изначально и будут развивать лучше",
                                "в будущеи.", sep=" "), reply_markup=add_skills_kb,
                        parse_mode=types.ParseMode.MARKDOWN)
        await state.finish()
        await AddSkillsForm.choosing.set()
