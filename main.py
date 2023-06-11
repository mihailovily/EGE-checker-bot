from functions import *
from telebot import types
import telebot
import os

# в settings/token.txt храним токен в settings/admin.txt - id админа (админов)
token = open('settings/token.txt').readline().split()[0]
bot = telebot.TeleBot(token)  # инит
admins = open('settings/admins.txt').read().split() # админы
print(admins)

@bot.message_handler(commands=['start', 'help'])  # старт
def send_welcome(message):
    usr_id = str(message.from_user.id)  # userid
    usr_name = str(message.from_user.first_name)  # имя юзера
    keyboard = types.ReplyKeyboardMarkup(True)  # генерируем клаву
    button_parse = types.KeyboardButton(text='Распарсить')
    button_get = types.KeyboardButton(text='Запросить результат')
    keyboard.add(button_parse)
    keyboard.add(button_get)
    bot.reply_to(message, "Привет, " + str(message.from_user.first_name) + '\n' + "Я могу распарсить json, взятый с https://checkege.rustest.ru/api/exam. Просто нажми кнопку и следуй инструкции.", reply_markup=keyboard)  # здороваемся

@bot.message_handler(commands=['parse'])
@bot.message_handler(regexp="Распарсить")
def find(message):
    message = bot.reply_to(message, 'Пришли текст')
    bot.register_next_step_handler(message, parse)
    # bot.register_next_step_handler(message, result_back)
def parse(message):
    usr_id = str(message.from_user.id)
    y = json.loads(message.text)
    answer = parse_result(y)
    if usr_id in admins:
        bot.reply_to(message, answer)


@bot.message_handler(commands=['getres'])
@bot.message_handler(regexp="Запросить результат")
def ask(message):
    global token
    usr_id = str(message.from_user.id)
    if usr_id in admins:
        bot.reply_to(message, 'Запрашиваю капчу, жди.')
        token = get_captcha()
        print(token)
        img = open('captcha/captcha.jpg', 'rb')
        bot.send_photo(usr_id, img)
        bot.register_next_step_handler(message, get_res)
    

def get_res(message):
    global captcha_answer
    captcha_answer = message.text
    usr_id = str(message.from_user.id)
    os.remove('captcha/captcha.jpg')
    bot.reply_to(message, 'Ответ записан. Ищу твои результаты.')
    with open("users/base.json", "r") as read_file:
        db = json.load(read_file)
    user = db[usr_id]
    results = get_results_from_site(user, token, captcha_answer)
    if usr_id in admins:
        bot.reply_to(message, results)


# если сообщение не распознано
@bot.message_handler(func=lambda message: True)
def answer(message):
    usr_id = str(message.from_user.id)
    if usr_id in admins:
        bot.reply_to(message, 'Я тебя не понял')
    
    


if __name__ == '__main__':
    bot.infinity_polling()
