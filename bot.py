import telebot
from me import get_me
from flask import Flask, request, abort
from query_log import logging
from datetime import datetime as dt
from os.path import exists
# https://core.telegram.org/bots/api Telegram Bot API


LUTZPYBOT = "5598132169:AAFBpUn4Us8m7StkY4yHUIcEnnJg3adPvsQ"


app = Flask(__name__)
bot = telebot.TeleBot(LUTZPYBOT)

print("LutzPyBot is working!")


@bot.message_handler(commands=['rules', 'faq'])
def send_lutz_command(message):
    bot.send_message(message.chat.id,
                     '<b>🟡 <u><a href="https://telegra.ph/pythonchatru-07-07">Правила чата</a></u></b>',
                     parse_mode='HTML',
                     disable_notification=True,
                     )
    logging(message)


@bot.message_handler(commands=['lutz'])
def send_lutz_command(message):
    bot.send_document(
        message.chat.id,
        document='BQACAgQAAxkBAAPBYsWJG9Ml0fPrnbU9UyzTQiQSuHkAAjkDAAIstCxSkuRbXAlcqeQpBA',
        caption="""<i><b>Learning Python</b>, 5th Edition</i>
    ├ by Mark Lutz
    └ Released June 2013""",
        parse_mode='HTML')
    logging(message)


@bot.message_handler(commands=['start'])
def send_start_notify_admin(message):
    bot.send_message(
        280887861, get_me(message), parse_mode='HTML')
    logging(message)


@bot.message_handler(commands=['log'])
def send_log_file(message):
    """Get log.csv"""
    if message.from_user.id == 280887861:
        file_path = f"logs/log_{dt.now().strftime('%Y-%m')}.csv"
        if exists(file_path):
            with open(file_path, "r", encoding='utf-8') as f:
                bot.send_document(message.chat.id, f)


@bot.inline_handler(lambda query: len(query.query) == 0)
def default_query(inline_query):

    """Inline Aricles"""
    lutz_rus = telebot.types.InlineQueryResultCachedDocument(
        id='44', title='📕 Изучаем Python 🇷🇺',
        document_file_id='BQACAgIAAxkBAAIBcGLHE2ryQewEP1ddXOd_jF3OOHUfAAISIAACaOk4SissgGKstQbqKQQ',
        description='Марк Лутц, 5-е издание, Том 1',
        caption="""<i><b>Изучаем Python</b>, 5-е издание</i>
        ├ Автор: Марк Лутц
        └ Год: 2019""",
        parse_mode='HTML',
        )

    matthes_rus = telebot.types.InlineQueryResultCachedDocument(
        id='45', title='📕 Изучаем Python 🇷🇺',
        document_file_id='BQACAgIAAxkBAAIBdmLHF0InnLNlQuKzi1fZOYWOdu7eAAIrIAACaOk4StPj0vlMzwe2KQQ',
        description='Эрик Мэтиз , 3-е издание',
        caption="""<i><b>Изучаем Python</b>, 3-е издание</i>
        ├ Автор: Эрик Мэтиз
        └ Год: 2020""",
        parse_mode='HTML',
        )

    lutz = telebot.types.InlineQueryResultDocument(
        id='1', title='📕 Learning Python ⭐️',
        document_url='https://fk7.ru/books/OReilly.Learning.Python.5th.Edition.pdf',
        description='Mark Lutz, 5th Edition',
        caption="""<i><b>Learning Python</b>, 5th Edition</i>
    ├ by Mark Lutz
    └ Released June 2013""",
        parse_mode='HTML',
        mime_type='application/pdf',
        thumb_url='https://fk7.ru/books/OReilly.Learning.Python.5th.Edition.jpg',)

    matthes = telebot.types.InlineQueryResultDocument(
        id='2', title='📕 Python Crash Course',
        document_url='https://fk7.ru/books/PythonCrashCourse.pdf',
        description='Eric Matthes, 2th Edition',
        caption="""<i><b>Python Crash Course</b>, 2th Edition</i>
    ├ by Eric Matthes
    └ Released 2019""",
        parse_mode='HTML',
        mime_type='application/pdf',
        thumb_url='https://fk7.ru/books/PythonCrashCourse.jpg',)

    vincent = telebot.types.InlineQueryResultDocument(
        id='3', title='📕 Django for Beginners',
        document_url='https://fk7.ru/books/django_for_beginners_4_0.pdf',
        description='William S. Vincent, 4.0',
        caption="""<i><b>Django for Beginners</b>, 4.0</i>
    ├ by William S. Vincent
    └ Released March 2022""",
        parse_mode='HTML',
        mime_type='application/pdf',
        thumb_url='https://fk7.ru/books/django_for_beginners_4_0.jpg',)

    bot.answer_inline_query(
        inline_query.id, [lutz,  matthes, lutz_rus, matthes_rus],
        cache_time=10)


@bot.message_handler(content_types=['document'])
def command_me(message):
    """GetMe Informer"""
    if message.chat.id == 280887861:
        bot.send_message(message.chat.id, message.document)


@bot.message_handler(commands=['me'])
def command_me(message):
    """GetMe Informer"""
    bot.send_message(message.chat.id, get_me(message), parse_mode='HTML')
    logging(message)


@app.route(f'/bot{LUTZPYBOT}/', methods=['POST'])
def webhook():
    """Parse POST requests from Telegram"""
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)
