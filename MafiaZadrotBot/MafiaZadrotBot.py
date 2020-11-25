from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from settings import TG_API_URL, TG_TOKEN
from handlers import *
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO, filename='bot.log')

def main():
    """Соединение бота с Телеграмм"""
    #переменная для взаимодействия с ботом
    my_bot = Updater(TG_TOKEN, TG_API_URL, use_context=True)
    logging.info('Start bot')
    my_bot.dispatcher.add_handler(CommandHandler('start', sms))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Начать'), sms))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Анекдот'), get_joke))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.contact, get_contact))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.location, get_location))
    my_bot.dispatcher.add_handler(ConversationHandler(entry_points=[MessageHandler(Filters.regex('Заполнить анкету'), form_start)],
                                                      states={"user_name": [MessageHandler(Filters.text, form_get_name)],
                                                              "user_age": [MessageHandler(Filters.text, form_get_age)],
                                                              "evaluation": [MessageHandler(Filters.regex('1|2|3|4|5'), form_get_evaluation)],
                                                              "comment": [MessageHandler(Filters.regex('Пропустить'), form_exit_comment),
                                                                          MessageHandler(Filters.text, form_comment)]},
                                                      fallbacks=[MessageHandler(Filters.text | Filters.video | Filters.photo | Filters.document, dontknow1)]))
    my_bot.dispatcher.add_handler(ConversationHandler(entry_points=[MessageHandler(Filters.regex('Узнать продажи'), get_sales)],
                                                      states={'region': [MessageHandler(Filters.text, get_region)]},
                                                      fallbacks=[MessageHandler(Filters.video | Filters.photo | Filters.document, dontknow2)]))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex('Картинки'), send_pics))
    my_bot.dispatcher.add_handler(ConversationHandler(entry_points=[MessageHandler(Filters.regex('Загрузить фото') | Filters.regex('Загрузить документ'), save_doc_start)],
                                                      states={'save_doc_photo_true': [MessageHandler(Filters.photo, save_doc_photo_end)],
                                                              'save_doc_document_true': [MessageHandler(Filters.document, save_doc_document_end)]},
                                                      fallbacks=[MessageHandler(Filters.text | Filters.video, dontknow3)]))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.text, parrot))
    my_bot.start_polling() #проверяет наличие сообщений
    my_bot.idle() #бот будет работать пока, его не остановят

if __name__ == '__main__':
    main()

