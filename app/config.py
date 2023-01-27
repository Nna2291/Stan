import os
import re
import logging
from flask import Flask
from telebot import TeleBot, logger, types
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
logging.critical('STAN STARTED!')

logger.setLevel(logging.DEBUG)
load_dotenv()

TOKEN = os.environ.get('LUTZPYBOT', 'Token not in ENVIRON')
bot = TeleBot(TOKEN, 'HTML', disable_web_page_preview=True, allow_sending_without_reply=True,
              colorful_logs=True)

app = Flask(__name__)

DATA = 'data/chat'

ADMIN_ID = 280887861  # Rykov7
PYTHONCHATRU = -1001338616632  # pythonchatru

URL_RX = re.compile(r'\w+\.\w+/\w+')
ALLOWED_WORDS = ['paste', 'nekobin', 'github', 'google', 'nometa', 'python', 'django', 'flask', 'fastapi', 'wiki',
                 'stackoverflow', 'habr', 'medium', 'youtu', 'stepik', 'telegraph', '#rtfm', 'support']

WHITEUN = set(os.environ.get('whitelist', '<<<ERR_USRS').split(','))
WHITEIDS = {int(i) for i in os.environ.get('whiteids', '<<<ERR_IDS').split(',')}

RUS = """ёйцукенгшщзхъфывапролджэячсмитьбю.Ё!"№;%:?ЙЦУКЕНГШЩЗХЪ/ФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,"""
ENG = """`qwertyuiop[]asdfghjkl;'zxcvbnm,./~!@#$%^&QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?"""
RUS_ENG_TABLE = str.maketrans(RUS, ENG)
ENG_RUS_TABLE = str.maketrans(ENG, RUS)

RULES = types.InlineKeyboardButton('🟡 Правила чата', url='https://telegra.ph/pythonchatru-07-07')
FAQ = types.InlineKeyboardButton('🔵 Частые вопросы', url='https://telegra.ph/faq-10-07-4')
LIB = types.InlineKeyboardButton('📚 Книги', url='https://telegra.ph/what-to-read-10-06')

SPAM = ['me.sv/', 'tg.sv/', 'goo.by/', 'go.sv/', 'intim.video/', 'uclck.ru/']
NON_GRATA = ['дудар', 'хауди', 'dudar']
BAN_WORDS = ['GREEN']

ZEN = ['Beautiful is better than ugly.', 'Explicit is better than implicit.', 'Simple is better than complex.',
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
