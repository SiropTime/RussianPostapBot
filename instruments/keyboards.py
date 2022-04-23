from aiogram import types

from instruments.utility import MENU_BUTTONS, PROFILE_BUTTONS, MASTER_BUTTONS
from telegram import player

add_skills_kb = types.InlineKeyboardMarkup(row_width=3)

add_skills_btns = dict([(x, types.InlineKeyboardButton(text=x, callback_data=x)) for x in player.add_skills.keys()])
add_skills_btns["exit"] = types.InlineKeyboardButton(text="❌ Завершить", callback_data="end")

button_list = dict([(x, types.InlineKeyboardButton(text=x, callback_data=x)) for x in player.add_skills.keys()])
button_list["exit"] = types.InlineKeyboardButton(text="❌ Завершить", callback_data="end")
add_skills_kb.add(*list(button_list.values()))

lvl_up_kb = types.InlineKeyboardMarkup(row_width=3)
btn_list = dict([(x, types.InlineKeyboardButton(text=x, callback_data=x)) for x in player.add_skills.keys()])
btn_list["exit"] = types.InlineKeyboardButton(text="❌ Завершить", callback_data="end")
lvl_up_kb.add(*list(btn_list.values()))

main_menu_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_kb.add(*MENU_BUTTONS)

profile_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
profile_kb.add(*PROFILE_BUTTONS)

gamemaster_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
gamemaster_kb.add(*MASTER_BUTTONS)

check_skill_btn = types.InlineKeyboardButton(text="🎲 Проверить навык!", callback_data="check")
check_skill_kb = types.InlineKeyboardMarkup(row_width=1)
check_skill_kb.add(check_skill_btn)
