import game
from aiogram import types

add_skills_kb = types.InlineKeyboardMarkup(row_width=3)

p = game.Player()
button_list = [types.InlineKeyboardButton(text=x, callback_data=x) for x in p.add_skills.keys()]
add_skills_kb.add(*button_list)