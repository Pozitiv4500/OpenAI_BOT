import datetime
import time

import jwt
import telebot
from telebot.types import InlineKeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup


from config import *

import psycopg2
bot = telebot.TeleBot(TOKEN)

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        options=f'-c search_path={schema_name}'
    )
    cursor = conn.cursor()
    print("Соединение с базой данных PostgreSQL установлено.")
except (Exception, psycopg2.DatabaseError) as error:
    print("Ошибка при подключении к базе данных PostgreSQL:", error)

def get_channel_link(channel_id):
    try:
        chat_info = bot.get_chat(channel_id)

        if chat_info.invite_link == None:
            print(chat_info)
            print('У канала нету пригласительтной ссылки!')
        else:
            return chat_info.invite_link
    except telebot.apihelper.ApiTelegramException:
        print('канал не найден')
def block(message):
    cursor = conn.cursor()
    cursor.execute('SELECT group_code FROM groups WHERE group_type = %s', ('reklam1',))
    channel_usernames = cursor.fetchall()
    user_id = message.from_user.id

    # Переменная для отслеживания, подписан ли пользователь на все каналы группы reklam1
    is_subscribed_to_all = True

    for channel_username in channel_usernames:
        user_info = bot.get_chat_member(channel_username, user_id)
        if user_info.status not in ["member", "administrator", "creator"]:
            is_subscribed_to_all = False
            break

    if is_subscribed_to_all:
        # Если пользователь подписан на все каналы, продолжаем выполнение
        return False
    else:
        markup = InlineKeyboardMarkup()

        # Если пользователь не подписан на все каналы, отправляем сообщение с просьбой подписаться

        for channel_username in channel_usernames:
            subscribe_button = InlineKeyboardButton(text=str(bot.get_chat(channel_username).title),url=str(get_channel_link(channel_username)))#ccылки на каналы
            markup.add(subscribe_button)
        subscribe_btn1 = InlineKeyboardButton("✅Подписался", callback_data="subscribed")
        markup.add(subscribe_btn1)
        bot.send_message(user_id, "Доступ к боту временно ограничен", reply_markup=ReplyKeyboardRemove())
        name = message.from_user.first_name
        bot.send_message(user_id, f"Хей, {name}, чтобы начать пользоваться ботом необходимо подписаться на наши каналы.", reply_markup=markup)
        return True

def block2hrs(message):
    user_id = message.from_user.id
    cursor = conn.cursor()
    cursor.execute("SELECT referral_date FROM referral_system WHERE user_id = %s;", (user_id,))
    user_registration_time = cursor.fetchone()[0]
    current_time = datetime.datetime.now()
    time_difference = current_time - user_registration_time
    if time_difference.total_seconds() >= 2 * 3600:#2*3600

        cursor = conn.cursor()
        cursor.execute('SELECT group_code FROM groups WHERE group_type = %s', ('reklam2',))
        channel_usernames = cursor.fetchall()


        # Переменная для отслеживания, подписан ли пользователь на все каналы группы reklam1
        is_subscribed_to_all = True

        for channel_username in channel_usernames:
            user_info = bot.get_chat_member(channel_username, user_id)
            if user_info.status not in ["member", "administrator", "creator"]:
                is_subscribed_to_all = False
                break

        if is_subscribed_to_all:
            # Если пользователь подписан на все каналы, продолжаем выполнение
            return False
        else:
            markup = InlineKeyboardMarkup()

            # Если пользователь не подписан на все каналы, отправляем сообщение с просьбой подписаться

            for channel_username in channel_usernames:
                if get_channel_link(channel_username) == None:
                    pass
                else:
                    subscribe_button = InlineKeyboardButton(text=str(bot.get_chat(channel_username).title),url=str(bot.get_chat(channel_username).invite_link))#ccылки на каналы
                    markup.add(subscribe_button)
            subscribe_btn1 = InlineKeyboardButton("✅Подписался", callback_data="subscribed1")
            markup.add(subscribe_btn1)
            name = message.from_user.first_name
            bot.send_message(user_id, "Доступ к боту временно ограничен", reply_markup=ReplyKeyboardRemove())
            bot.send_message(user_id, f"Хей, {name}, подпишись на другие наши каналы, чтобы продолжить", reply_markup=markup)
            return True
    else:
        return False


JWT_SECRET = "ВАШ_СЕКРЕТНЫЙ_КЛЮЧ"

def generate_jwt_token():
    payload = {
        'iat': int(time.time()),
        'exp': int(time.time()) + 3600,  # Токен будет действителен в течение 1 часа
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return token
