import game
from aiogram import types
from utility import MENU_BUTTONS

add_skills_kb = types.InlineKeyboardMarkup(row_width=3)

p = game.Player()
button_list = dict([(x, types.InlineKeyboardButton(text=x, callback_data=x)) for x in p.add_skills.keys()])
button_list["exit"] = types.InlineKeyboardButton(text="Завершить", callback_data="end")
add_skills_kb.add(*list(button_list.values()))

main_menu_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_kb.add(*MENU_BUTTONS)
