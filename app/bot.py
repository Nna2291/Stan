import shelve
from datetime import datetime as dt
from flask import Flask, request, abort
from telebot import types
import logging
from urllib import parse

from . import stan
from . import reminder
from . import admin
from . import report
from .config import bot, URL_RX, ALLOWED_WORDS, ADMIN_ID, TOKEN, PYTHONCHATRU, WHITEUN, WHITEIDS, RUS_ENG_TABLE, \
    ENG_RUS_TABLE, RUS
from .me import get_me

# https://core.telegram.org/bots/api Telegram Bot API
# https://github.com/eternnoir/pyTelegramBotAPI/tree/master/examples

logging.basicConfig(level=logging.INFO, format='%(message)s')
app = Flask(__name__)

logging.warning('>>> PYBOT STARTED!')

zen_rows = ['Beautiful is better than ugly.', 'Explicit is better than implicit.', 'Simple is better than complex.',
            'Complex is better than complicated.', 'Flat is better than nested.', 'Sparse is better than dense.',
            'Readability counts.',
            "Special cases aren't special enough to break the rules. Although practicality beats purity.",
            'Errors should never pass silently. Unless explicitly silenced.',
            'In the face of ambiguity, refuse the temptation to guess.',
            'There should be one — and preferably only one — obvious way to do it.',
            'Now is better than never. Although never is often better than *right* now.',
            "If the implementation is hard to explain, it's a bad idea.",
            'If the implementation is easy to explain, it may be a good idea.',
            "Namespaces are one honking great idea — let's do more of those!"]


@bot.message_handler(commands=['start'])
def start(message: types.Message):
    """ Start """
    log_msg = f'[START] {message.from_user.id} {message.from_user.first_name}'
    if message.from_user.last_name:
        log_msg += f' {message.from_user.last_name}'
    logging.warning(log_msg)


def check_spam_list(type_message: types.Message) -> bool:
    """ Check for mentioning unwanted persons in text. """
    if type_message.from_user.username not in WHITEUN and type_message.from_user.id not in WHITEIDS:
        spam_urls = ['me.sv/', 'tg.sv/', 'goo.by/', 'go.sv/', 'intim.video/',
                     'uclck.ru/']
        for url in spam_urls:
            if url in type_message.text.casefold():
                return True


@bot.edited_message_handler(func=check_spam_list)
@bot.message_handler(func=check_spam_list)
def moderate_messages(message: types.Message):
    """ Ban user and delete their message. """
    logging.warning(f'[BAN] {message.from_user.id} {message.from_user.username} - {message.text}')
    bot.delete_message(message.chat.id, message.id)
    bot.ban_chat_member(message.chat.id, message.from_user.id)
    if message.chat.id == PYTHONCHATRU:
        with shelve.open('chat_stats') as chat_stats:
            chat_stats['Banned'] += 1


def check_caption_spam_list(type_message: types.Message) -> bool:
    """ Check for mentioning unwanted words in caption. """
    unwanted_phrases = ['GREEN ROOM']
    for phrase in unwanted_phrases:
        if type_message.caption and phrase in type_message.caption:
            return True


@bot.message_handler(func=check_caption_spam_list, content_types=['video'])
def catch_videos(message: types.Message):
    """Catch offensive videos"""
    logging.warning(f'[BAN] {message.from_user.id} {message.from_user.first_name} - {message.video.file_name}')
    bot.delete_message(message.chat.id, message.id)
    bot.ban_chat_member(message.chat.id, message.from_user.id)
    with shelve.open('chat_stats') as chat_stats:
        chat_stats['Banned'] += 1


def check_no_allowed(word_list, msg):
    for word in word_list:
        if word in msg.casefold():
            return False
    return True


def check_delete_list(type_message: types.Message) -> bool:
    """ Check for URLs in message and delete. """
    if type_message.from_user.username not in WHITEUN and type_message.from_user.id not in WHITEIDS:
        if URL_RX.search(type_message.text) and check_no_allowed(ALLOWED_WORDS, type_message.text):
            logging.info(f'[DEL] {type_message.from_user.id} {type_message.from_user.first_name} - {type_message.text}')
            return True
        if type_message.entities:
            for entity in type_message.entities:
                if entity.url and check_no_allowed(ALLOWED_WORDS, entity.url):
                    logging.info(
                        f'[DEL] {type_message.from_user.id} {type_message.from_user.first_name} - Entity ({entity.url})')
                    return True


@bot.edited_message_handler(func=check_delete_list)
@bot.message_handler(func=check_delete_list)
def delete_message(message: types.Message):
    """ Delete unwanted message. """
    bot.delete_message(message.chat.id, message.id)
    if message.chat.id == PYTHONCHATRU:
        with shelve.open('chat_stats') as chat_stats:
            chat_stats['Deleted'] += 1


@bot.message_handler(commands=['rules'])
def send_lutz_command(message):
    """ Send Chat Rules link. """
    logging.warning('Sent Rules link')
    bot.reply_to(message,
                 '<b>🟡 <u><a href="https://telegra.ph/pythonchatru-07-07">Правила чата</a></u></b>',
                 parse_mode='HTML',
                 )


@bot.message_handler(commands=['faq'])
def send_lutz_command(message):
    """ Send Chat FAQ link. """
    logging.warning('Sent FAQ link')
    bot.reply_to(message,
                 '<b>🔵 <u><a href="https://telegra.ph/faq-10-07-4">FAQ</a></u></b>',
                 parse_mode='HTML',
                 )


@bot.message_handler(commands=['lutz'])
def send_lutz_command(message):
    """ Send the Lutz's Book. """
    logging.warning('Send the Lutz Book')
    bot.send_document(
        message.chat.id,
        document='BQACAgQAAxkBAAPBYsWJG9Ml0fPrnbU9UyzTQiQSuHkAAjkDAAIstCxSkuRbXAlcqeQpBA',
        caption="вот, не позорься")


@bot.message_handler(commands=['bdmtss'])
def send_bdmtss_audio(message):
    bot.send_voice(message.chat.id, 'AwACAgIAAxkBAAIJrWOg2WUvLwrf7ahyJxQHB8_nqllwAAL5JQAC2_IJSbhfQIO5YnVmLAQ')


@bot.message_handler(commands=['tr'])
def translate_layout(message):
    if message.reply_to_message and message.reply_to_message.text:
        if message.reply_to_message.text[0] in RUS:
            bot.send_message(message.chat.id, message.reply_to_message.text.translate(RUS_ENG_TABLE))
        else:
            bot.send_message(message.chat.id, message.reply_to_message.text.translate(ENG_RUS_TABLE))


@bot.message_handler(commands=['lib', 'library', 'book', 'books'])
def send_lutz_command(message):
    """ Send Chat's Library link. """
    logging.warning('Send Library link')
    bot.reply_to(message,
                 '📚 <b><u><a href="https://telegra.ph/what-to-read-10-06">Библиотека питониста</a></u></b>',
                 parse_mode='HTML',
                 disable_notification=True,
                 )


@bot.inline_handler(lambda query: True)
def default_query(inline_query):
    """ Inline the Zen of Python. """
    zen = []
    for id_p, phrase in enumerate(zen_rows):
        q = inline_query.query.casefold()
        if phrase.casefold().startswith(q) or ' ' + q in phrase.casefold():
            zen.append(types.InlineQueryResultArticle(
                f"{id_p + 7000}", f'The Zen of Python #{id_p + 1}', types.InputTextMessageContent(
                    f"<i>{phrase}</i>", parse_mode='HTML'), description=phrase))

    bot.answer_inline_query(inline_query.id, zen, cache_time=1200)


@bot.message_handler(commands=['me'])
def command_me(message):
    """ Send info about user and chat id [Service]. """
    bot.send_message(message.chat.id, get_me(message), parse_mode='HTML')


@bot.message_handler(commands=['remind'])
def remind_manually(message):
    """ Remind holidays manually. """
    args = message.text.split()
    if len(args) > 1:
        try:
            today = dt.strptime(args[1], "%m-%d-%Y")
        except ValueError as ve:
            bot.send_message(message.chat.id, f"Не удалось разобрать дату!\n{ve}", parse_mode='HTML')
        else:
            reminder.remind(message.chat.id, today)
    else:
        bot.send_message(message.chat.id, f"<b>Формат даты: MM-DD-YYYY</b>\n\n"
                                          f"Примеры:\n"
                                          f"/remind 09-12-2024\n"
                                          f"/remind 09-13-2022", parse_mode='HTML')


@bot.message_handler(commands=['jobs'])
def list_jobs(message):
    """ List all the jobs in schedule. """
    if message.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, reminder.print_get_jobs(),
                         parse_mode='HTML', disable_web_page_preview=True)


@bot.message_handler(commands=['stats'])
def send_stats(message):
    bot.send_message(message.chat.id, report.create_report_text(),
                     parse_mode='HTML', disable_web_page_preview=True)


@bot.message_handler(commands=['add'])
def add_stan_quote(message):
    if message.reply_to_message and message.reply_to_message.text:
        with open('Stan.txt', 'a', encoding='utf8') as stan_quotes:
            stan_quotes.write('\n' + message.reply_to_message.text)
            bot.send_message(message.chat.id, f'Добавил: {message.reply_to_message.text}',
                             parse_mode='HTML', disable_web_page_preview=True)


@bot.message_handler(commands=['quote'])
def stan_speak(message):
    bot.send_message(message.chat.id, stan.speak(0))


@bot.message_handler(commands=['reset_stats'])
def send_stats(message):
    report.reset_report_stats()
    bot.send_message(message.chat.id, report.reset_report_stats(),
                     parse_mode='HTML', disable_web_page_preview=True)


@bot.message_handler(commands=['reload'])
def send_stats(message):
    admin.reload_modules()
    bot.send_message(message.chat.id, 'Reloaded successfully')


@bot.message_handler(func=lambda a: a.from_user.id == ADMIN_ID, commands=['pydel', 'pyban', 'unban_id'])
def admin_panel(message: types.Message):
    """ Admin panel. """
    if message.text == '/pydel' and message.reply_to_message:
        bot.delete_message(message.chat.id, message.id)
        bot.delete_message(message.chat.id, message.reply_to_message.id)
        logging.warning(
            f'[DEL (M)] {message.reply_to_message.from_user.id} {message.reply_to_message.from_user.first_name} - {message.reply_to_message.text}')
    elif message.text == '/pyban' and message.reply_to_message:
        bot.delete_message(message.chat.id, message.id)
        bot.delete_message(message.chat.id, message.reply_to_message.id)
        bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        logging.warning(
            f'[BAN (M)] {message.reply_to_message.from_user.id} {message.reply_to_message.from_user.first_name} - {message.reply_to_message.text}')
    elif message.text.split()[0] == '/unban_id' and message.text.split()[-1].isdigit():
        unban_id = int(message.text.split()[-1])
        bot.unban_chat_member(PYTHONCHATRU, unban_id)
        logging.warning(f'[UNBAN (M)] {unban_id}')


@bot.message_handler(commands=['tsya'])
def send_tsya_link(message: types.Message):
    """ тся/ться """
    answer = '<a href="https://tsya.ru/">-тся/-ться</a>'
    if message.reply_to_message:
        bot.reply_to(message.reply_to_message, answer, parse_mode='HTML', disable_web_page_preview=True)
    else:
        bot.send_message(message.chat.id, answer, parse_mode='HTML', disable_web_page_preview=True)


@bot.message_handler(commands=['nojob'])
def send_no_job(message):
    logging.warning('Sent no job')
    answer = """Мы здесь не для того, чтобы за тебя решать задачи.

Здесь помогают по конкретным вопросам <u>в ТВОЁМ</u> коде, поэтому тебе нужно показать код, который ты написал сам и объяснить где и почему застрял... всё просто. 🤷🏻‍♂️"""
    if message.reply_to_message:
        bot.reply_to(message.reply_to_message, answer, parse_mode='HTML', disable_web_page_preview=True)
    else:
        bot.send_message(message.chat.id, answer, parse_mode='HTML', disable_web_page_preview=True)


@bot.message_handler(commands=['nometa'])
def send_nometa(message: types.Message):
    """ No meta """
    answer = 'Пожалуйста, не задавайте <a href="https://nometa.xyz/ru.html">мета-вопросов</a> в чате!'
    if message.reply_to_message:
        bot.reply_to(message.reply_to_message, answer, parse_mode='HTML', disable_web_page_preview=True)
    else:
        bot.send_message(message.chat.id, answer, parse_mode='HTML', disable_web_page_preview=True)


@bot.message_handler(commands=['neprivet'])
def send_neprivet(message: types.Message):
    """ Neprivet. """
    answer = '<a href="https://neprivet.com/">Непривет</a>'
    if message.reply_to_message:
        bot.reply_to(message.reply_to_message, answer, parse_mode='HTML', disable_web_page_preview=True)
    else:
        bot.send_message(message.chat.id, answer, parse_mode='HTML', disable_web_page_preview=True)


"""
Caution commands: nobot, noparse, nogui
"""


@bot.message_handler(commands=['nobot'])
def nobot(message: types.Message):
    answer = """<b>Внимание</b>:
Телеграм бот <i>не должен</i> быть твоим первым проектом на Python. Пожалуйста, изучи <code>основы Python</code>, <code>работу с модулями</code>, <code>основы веб-технологий</code>, <code>асинхронное программирование</code> и <code>отладку</code> до начала работы с Телеграм ботами. Существует много ресурсов для этого в интернете."""
    if message.reply_to_message:
        bot.reply_to(message.reply_to_message, answer, parse_mode='HTML', disable_web_page_preview=True)
    else:
        bot.send_message(message.chat.id, answer, parse_mode='HTML', disable_web_page_preview=True)


@bot.message_handler(commands=['nogui'])
def nogui(message: types.Message):
    answer = """<b>Внимание</b>:
GUI приложение <i>не должно</i> быть твоим первым проектом на Python. Пожалуйста, изучи <code>основы Python</code>, <code>работу с модулями</code>, <code>циклы событий</code> и <code>отладку</code> до начала работы с какими-либо GUI-фреймворками. Существует много ресурсов для этого в интернете."""
    if message.reply_to_message:
        bot.reply_to(message.reply_to_message, answer, parse_mode='HTML', disable_web_page_preview=True)
    else:
        bot.send_message(message.chat.id, answer, parse_mode='HTML', disable_web_page_preview=True)


@bot.message_handler(commands=['g'])
def google_it(message: types.Message):
    """ Google it! """
    search_engine = 'https://www.google.ru/search?q='
    if message.reply_to_message and message.reply_to_message.text:
        if len(message.text.split()) == 1:
            r = parse.quote_plus(message.reply_to_message.text)
        else:
            r = parse.quote_plus(' '.join(message.text.split()[1:]))
        bot.reply_to(message.reply_to_message, f"{search_engine}{r}",
                     disable_web_page_preview=True)
    else:
        if len(message.text.split()) > 1:
            r = parse.quote_plus(' '.join(message.text.split()[1:]))
            bot.reply_to(message, f"{search_engine}{r}", disable_web_page_preview=True)


""" Tease for blogger mentions. """


def check_unwanted_list(type_message: types.Message) -> bool:
    """ Check for bloggers. """
    unwanted_phrases = ['дудар', 'хауди', 'dudar']
    for phrase in unwanted_phrases:
        if phrase in type_message.text.casefold():
            return True


@bot.message_handler(func=check_unwanted_list)
def unwanted_mentions(message: types.Message):
    """ Reply to unwanted mentions. """
    bot.reply_to(message, f'у нас тут таких не любят')


def check_chat(message: types.Message):
    if message.chat.id == PYTHONCHATRU:
        return True


@bot.message_handler(func=check_chat, content_types=['text', 'sticker', 'photo', 'animation', 'video',
                                                     'audio', 'document'])
def unwanted_mentions(message: types.Message):
    """ Count messages. """
    with shelve.open('chat_stats', writeback=True) as s:
        if message.from_user.id not in s['Messages']:
            s['Messages'][message.from_user.id] = {'User': message.from_user, 'Count': 0}
            logging.warning(f'New counter: {message.from_user.id} - {message.from_user.first_name}')
        else:
            s['Messages'][message.from_user.id]['Count'] += 1

    quote = stan.speak(20)
    if quote:
        bot.send_message(message.chat.id, quote)


@app.route(f"/bot{TOKEN}/", methods=['POST'])
def webhook():
    """ Parse POST requests from Telegram. """
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)
