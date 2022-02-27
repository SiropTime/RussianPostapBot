import telebot as tb
from game import *
from game_utils import *

bot = tb.TeleBot("5218155011:AAF0GYeUQtMswyMXHhsULlrLHlnQrphEpA8")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/start":
        bot.send_message(message.chat.id, "Маслину словил " + str(message.chat.id))
        player = Player()
        player.id = int(message.chat.id)

@bot.message_handler(commands=['create_player'])
def create_player(message):
    bot.send_message(message.chat.id, "Создание игрока")


if __name__ == "__main__":
    game = Game()
    bot.polling(none_stop=True)
