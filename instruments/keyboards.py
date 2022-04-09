from aiogram import types

from instruments.utility import MENU_BUTTONS, PROFILE_BUTTONS
from telegram import player

add_skills_kb = types.InlineKeyboardMarkup(row_width=3)

button_list = dict([(x, types.InlineKeyboardButton(text=x, callback_data=x)) for x in player.add_skills.keys()])
button_list["exit"] = types.InlineKeyboardButton(text="× Завершить", callback_data="end")
add_skills_kb.add(*list(button_list.values()))

main_menu_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_kb.add(*MENU_BUTTONS)

profile_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
profile_kb.add(*PROFILE_BUTTONS)
