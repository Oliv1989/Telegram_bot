from telegram import ReplyKeyboardMarkup, KeyboardButton
import os
from settings import FILES_PATH

SMILE = ['😊', '😀', '😇', '🤠', '😎', '🤓', '👶', '🧑‍🚀', '👮', '🦸', '🧟']

def get_keyboard():
    """Функция добавления кнопки"""
    contact_button = KeyboardButton('Отправить контакты', request_contact=True)
    location_button = KeyboardButton('Отправить геолокацию', request_location=True)
    my_keyboard = ReplyKeyboardMarkup([['Анекдот','Начать'],
                                       [contact_button, location_button],
                                       ['Заполнить анкету', 'Загрузить фото'],
                                       ['Картинки', 'Узнать продажи'],
                                       ['Загрузить документ']], resize_keyboard=True)
    return my_keyboard

def check_name(name):
    number = 1
    while name in os.listdir(FILES_PATH):
        name = [x for x in list(name) if not x.isdigit()]
        name = ''.join(x for x in name)
        name = name.split('.')[0] + str(number) + '.' + name.split('.')[1]
        number = int(number) + 1
    return name
