import requests
from bs4 import BeautifulSoup
from utils import get_keyboard, SMILE, check_name
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, ParseMode, File, Bot
from telegram.ext import ConversationHandler, Filters
import glob
from random import choice
from emoji import emojize
from mongodb import mdb, search_or_save_user, save_user_form
import pandas as pd
from settings import TG_TOKEN, FILES_PATH
import os

def sms(bot, update):
    """Функция вызывается при отправке команды /start"""
    user = search_or_save_user(mdb, bot.effective_user, bot.message)
    smile = emojize(choice(SMILE), use_aliases=True)
    bot.message.reply_text('Привет {} {}'.format(bot.message.chat.first_name, smile), reply_markup=get_keyboard())

def send_pics(bot, update):
    lists = glob.glob('images/*')
    picture = choice(lists)
    update.bot.send_photo(chat_id=bot.message.chat.id, photo=open(picture, 'rb'))


def get_joke(bot, update):
    """Функция вызывается при отправке сообщения Анекдот"""
    receive = requests.get('http://anekdotme.ru/random') #отправляем запрос к странице
    page = BeautifulSoup(receive.text, 'html.parser') #подключаем html парсер, получаем текст страницы
    find = page.select('.anekdot_text') #из страницы html получаем class='anekdot_text'
    for text in find:
        page = (text.getText().strip()) #из class='anekdot_text' получаем текст и убираем пробелы по сторонам
    bot.message.reply_text(page)

def get_contact(bot, update):
    """Функция отвечает пользователю о получении контактов"""
    print(bot.message.contact)
    bot.message.reply_text('{}, мы получили ваш номер телефона'.format(bot.message.chat.first_name))

def get_location(bot, update):
    """Функция отвечает пользователю о получении местоположения"""
    print(bot.message.location)
    bot.message.reply_text('{}, мы получили ваше местоположение'.format(bot.message.chat.first_name))

def parrot(bot, update):
    """Функция отвечает пользователю тем же сообщением, что пользователь отправил"""
    print(bot.message.text)
    bot.message.reply_text(bot.message.text)

def form_start(bot, update):
    bot.message.reply_text('Как вас зовут?', reply_markup=ReplyKeyboardRemove())
    return "user_name"

def form_get_name(bot, update):
    update.user_data['name'] = bot.message.text #временно сохраняем ответ
    bot.message.reply_text('Сколько вам лет?')
    return "user_age"

def form_get_age(bot, update):
    update.user_data['age'] = bot.message.text  # временно сохраняем ответ
    reply_keyboard = [['1', '2', '3', '4', '5']] #создаем клавиатуру
    bot.message.reply_text('Насколько вам понравился опрос?', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return "evaluation"

def form_get_evaluation(bot, update):
    update.user_data['evaluation'] = bot.message.text  # временно сохраняем ответ
    reply_keyboard = [['пропустить']]  # создаем клавиатуру
    bot.message.reply_text('Напишите отзыв или пропустите шаг?',
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return "comment"

def form_exit_comment(bot, update):
    update.user_data['comment'] = bot.message.text  # временно сохраняем ответ
    user = search_or_save_user(mdb, bot.effective_user, bot.message)  # получаем данные из БД
    save_user_form(mdb, user, update.user_data)  # передаем результаты анкеты
    text = """Результат опроса:
    <b>Имя:</b> {name}
    <b>Возраст:</b> {age}
    <b>Оценка:</b> {evaluation}
    """.format(**update.user_data)
    bot.message.reply_text(text, parse_mode=ParseMode.HTML)
    bot.message.reply_text('Спасибо за комментарии', reply_markup=get_keyboard())
    return ConversationHandler.END

def form_comment(bot, update):
    update.user_data['comment'] = bot.message.text  # временно сохраняем ответ
    user = search_or_save_user(mdb, bot.effective_user, bot.message) #получаем данные из БД
    form = save_user_form(mdb, user, update.user_data) #передаем и получаем результаты анкеты
    print(form)
    text = """Результат опроса:
    <b>Имя:</b> {name}
    <b>Возраст:</b> {age}
    <b>Оценка:</b> {evaluation}
    <b>Комментарий:</b> {comment}
    """.format(**update.user_data)
    bot.message.reply_text(text, parse_mode=ParseMode.HTML)
    bot.message.reply_text('Спасибо за комментарии', reply_markup=get_keyboard())
    return ConversationHandler.END

def dontknow1(bot, update):
    bot.message.reply_text('Я вас не понимаю, выберите оценку на клавиатуре')

def dontknow2(bot, update):
    bot.message.reply_text('Я вас не понимаю, введите название региона')

def dontknow3(bot, update):
    bot.message.reply_text('Я вас не понимаю, вышлите фото или документ')

def get_sales(bot, update):
    bot.message.reply_text('Какой регион вас интересует?', reply_markup=ReplyKeyboardRemove())
    return "region"

def get_region(bot, update):
    update.user_data['region'] = bot.message.text  # временно сохраняем ответ
    df = pd.read_excel(r'C:\Users\Админ\PycharmProjects\MafiaZadrotBot\docs\sales.xlsx', sheet_name='Sheet1')
    text = f'Регион: {update.user_data["region"]}\n' \
        f'Объем продаж: {df.Sales_volume[df["Region"] == update.user_data["region"]].tolist()[0]}'
    bot.message.reply_text(text, reply_markup=get_keyboard())
    return ConversationHandler.END

def save_doc_start(bot, update):
    if bot.message.text == 'Загрузить фото':
        bot.message.reply_text('Я готов сохранить фото. Вышлите фото в ответ на это сообщение', reply_markup=ReplyKeyboardRemove())
        return 'save_doc_photo_true'
    else:
        bot.message.reply_text('Я готов сохранить документ. Вышлите документ в ответ на это сообщение', reply_markup=ReplyKeyboardRemove())
        return 'save_doc_document_true'

def save_doc_photo_end(bot, update):
    Bot.get_file(Bot(TG_TOKEN), bot.message.photo[0].file_id).download(os.path.join(FILES_PATH, check_name('new.jpg')))
    bot.message.reply_text('Ваше фото сохранено', reply_markup=get_keyboard())
    return ConversationHandler.END

def save_doc_document_end(bot, update):
    Bot.get_file(Bot(TG_TOKEN), bot.message.document.file_id).download(os.path.join(FILES_PATH, check_name(bot.message.document.file_name)))
    bot.message.reply_text('Ваш документ сохранен', reply_markup=get_keyboard())
    return ConversationHandler.END
