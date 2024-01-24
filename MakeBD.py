import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards import markup,markup1,markup2,markup3,markup4,markup5,markup6,markup7,markup8,markup9,markup10,markup11,markup12,admin
import yookassa
from config import *
import psycopg2
from telebot.types import Message
from telebot.types import LabeledPrice
bot = telebot.TeleBot(TOKEN)
import payment

conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        options=f'-c search_path={schema_name}'
    )
cursor = conn.cursor()




cursor.execute('''
    CREATE TABLE IF NOT EXISTS groups (
        group_code BIGINT PRIMARY KEY,
        group_type TEXT CHECK(group_type IN ('promo_chanel', 'reklam1', 'reklam2'))
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS prices (
    group_type TEXT CHECK(group_type IN ('qrypto', 'rub')),
    money TEXT,
    tokens BIGINT
);
''')
cursor.execute('''
        CREATE TABLE IF NOT EXISTS referral_system (
            user_id BIGINT PRIMARY KEY,
            is_referred BOOLEAN,
            invited_by BIGINT,
            referral_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS main_tg_user (
        telegram_id BIGINT PRIMARY KEY,
        name TEXT,
        balance BIGINT
    )
''')
cursor.execute('''
        CREATE TABLE IF NOT EXISTS main_keys (
            id SERIAL PRIMARY KEY,
            key VARCHAR(255) NOT NULL
        );
''')
conn.commit()
conn.close()
