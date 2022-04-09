from aiogram.types import ParseMode

from telegram import dp

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.dispatcher.filters.state import State
from emoji import emojize
from aiogram.utils import markdown as md

from handlers.add_skills_handlers import AddSkillsForm
from instruments.keyboards import add_skills_kb
from telegram import player, game


class MainSkillsForm(StatesGroup):
    physics = State()
    intelligence = State()
    perception = State()
    charisma = State()


@dp.message_handler(lambda msg: not msg.text.isdigit(),
                    state=[MainSkillsForm.physics, MainSkillsForm.intelligence, MainSkillsForm.perception,
                           MainSkillsForm.charisma])
async def process_skills_invalid(msg: types.Message):
    return await msg.reply(emojize(":no_entry_sign: Напишите количество очков ***цифрами***!", use_aliases=True),
                           parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(lambda msg: not (20 >= int(msg.text) > 0),
                    state=[MainSkillsForm.physics, MainSkillsForm.intelligence, MainSkillsForm.perception,
                           MainSkillsForm.charisma])
async def process_skills_limits(msg: types.Message):
    return await msg.reply(emojize(":no_entry_sign: Значение характеристики должно быть"
                                   " ***больше нуля*** и ***не больше 20***!", use_aliases=True),
                           parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(lambda msg: msg.text.isdigit(), state=MainSkillsForm.physics)
async def process_physics(msg: types.Message, state: FSMContext):
    await state.update_data(physics=int(msg.text))
    await MainSkillsForm.next()
    async with state.proxy() as data:
        sum_stats = data["physics"]
        await msg.answer("На данный момент сумма ваших характеристик равна: ***" + str(sum_stats) + "***",
                         parse_mode=ParseMode.MARKDOWN)
    await msg.answer(emojize("Введите количество очков :brain: ***интеллекта*** от 1 до 20:",
                             use_aliases=True),
                     parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(lambda msg: msg.text.isdigit(), state=MainSkillsForm.intelligence)
async def process_intelligence(msg: types.Message, state: FSMContext):
    await state.update_data(intelligence=int(msg.text))
    await MainSkillsForm.next()
    async with state.proxy() as data:
        sum_stats = data["physics"] + data["intelligence"]
        await msg.answer("На данный момент сумма ваших характеристик равна: ***" + str(sum_stats) + "***",
                         parse_mode=ParseMode.MARKDOWN)
    await msg.answer(emojize("Введите количество очков :eyes: ***восприятия*** от 1 до 20:",
                             use_aliases=True),
                     parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(lambda msg: msg.text.isdigit(), state=MainSkillsForm.perception)
async def process_perception(msg: types.Message, state: FSMContext):
    await state.update_data(perception=int(msg.text))
    await MainSkillsForm.next()
    async with state.proxy() as data:
        sum_stats = data["physics"] + data["intelligence"] + data["perception"]
        await msg.answer("На данный момент сумма ваших характеристик равна: ***" + str(sum_stats) + "***",
                         parse_mode=ParseMode.MARKDOWN)
    await msg.reply(emojize("Введите количество очков :bust_in_silhouette: ***харизмы*** от 1 до 20:",
                            use_aliases=True),
                    parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(lambda msg: msg.text.isdigit(), state=MainSkillsForm.charisma)
async def process_charisma(msg: types.Message, state: FSMContext):
    await state.update_data(charisma=int(msg.text))
    async with state.proxy() as data:
        print(data)
        skills = data["physics"] + data["intelligence"] + data["perception"] + data["charisma"]
        if skills > 45 or skills < 4:
            await msg.answer(emojize(":sos: Ваш персонаж неуравновешен, у него либо больше положенного, "
                                     "либо он инвалид."
                                     "\nПожалуйста, введите навыки заново!", use_aliases=True),
                             parse_mode=ParseMode.MARKDOWN)
            await state.finish()
            await MainSkillsForm.physics.set()
            await msg.answer(emojize("Введите количество очков :muscle: ***физической подготовки*** от 1 до 20:",
                                     use_aliases=True),
                             parse_mode=ParseMode.MARKDOWN)
        else:
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
