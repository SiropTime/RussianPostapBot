from telegram import dp

from contextlib import suppress

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import MessageNotModified

from instruments.keyboards import button_list, main_menu_kb, add_skills_kb

from telegram import player, game, bot

# Приоритетные навыки, выбранные пользователем
priority_skills = []


class AddSkillsForm(StatesGroup):
    choosing = State()


@dp.callback_query_handler(state=AddSkillsForm.choosing)
async def process_add_skills(callback_query: types.CallbackQuery, state=FSMContext):
    with suppress(MessageNotModified):
        if callback_query.data not in priority_skills and not callback_query.data == "end":
            if len(priority_skills) >= 5:
                await callback_query.answer(text="Вы уже выбрали 5 навыков! Уберите уже выбранные для изменения!",
                                            show_alert=True)
            else:
                button_list[callback_query.data].text = "☑ " + button_list[callback_query.data].text
                priority_skills.append(callback_query.data)
        elif callback_query.data in priority_skills:
            button_list[callback_query.data].text = button_list[callback_query.data].text[2:]
            priority_skills.remove(callback_query.data)
        elif callback_query.data == "end":
            if len(priority_skills) < 5:
                await callback_query.answer(text="Выберите 5 навыков!", show_alert=True)
            else:
                await callback_query.message.edit_text("Успешно!")
                player.priority_skills = priority_skills
                player.calculate_skills(game.cursor, game.db)
                print(player.add_skills)
                await state.finish()
                # await Menu.main.set()
                await bot.send_message(player.id, "Меню", reply_markup=main_menu_kb)

    print(priority_skills)

    await callback_query.message.edit_reply_markup(reply_markup=add_skills_kb)
    await callback_query.answer()
