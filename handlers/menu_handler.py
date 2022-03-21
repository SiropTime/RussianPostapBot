from telegram import *


class Menu(StatesGroup):
    main = State()
    profile = State()


@dp.message_handler(commands=['menu'])
async def menu(msg: types.Message):
    await msg.answer("Меню", reply_markup=main_menu_kb)
    await Menu.main.set()


@dp.message_handler()
async def process_menu(msg: types.Message):
    if msg.text == emojize(":clipboard: Профиль", use_aliases=True):
        await msg.answer("Профиль", parse_mode=ParseMode.MARKDOWN)
        await msg.answer(player.prepare_profile()[0])
        await msg.answer(player.prepare_profile()[1])


@dp.message_handler(state=Menu.main)
async def main_menu(msg: types.Message, state: FSMContext):
    pass
