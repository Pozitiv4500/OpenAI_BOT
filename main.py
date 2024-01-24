import base64
import datetime
import json
from io import BytesIO

import openai
import requests
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from helpers import block, get_channel_link, block2hrs, generate_jwt_token
from keyboards import markup, markup1, markup2, markup3, markup4, markup5, markup6, markup7, markup8, markup9, markup10, \
    markup11, markup12, admin, markup13, markup14, admin2, markup16, admin0, admin4, admin6, admin7, markup18, admin9
import yookassa
from config import *
import psycopg2
from telebot.types import Message
from telebot.types import LabeledPrice
bot = telebot.TeleBot(TOKEN)
import payment
import time
import random


try:
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        options=f'-c search_path={schema_name}'
    )
    print("Соединение с базой данных PostgreSQL установлено.")
except (Exception, psycopg2.DatabaseError) as error:
    print("Ошибка при подключении к базе данных PostgreSQL:", error)

def gpt_key():
    cursor = conn.cursor()
    key_query = "SELECT key FROM main_keys ORDER BY RANDOM() LIMIT 1;"
    cursor.execute(key_query)
    random_key = cursor.fetchone()

    from openai import OpenAI

    client = OpenAI(api_key=random_key[0])
    return client


@bot.message_handler(func=lambda message: message.chat.id == int(MAIN_CHANEL))
def handle_channel_message(message):
    if message.text.startswith('/gpt'):
        chat_id = message.chat.id
        query = message.text.replace('/gpt', '')  # Удаление "/gpt" и пробелов
        msg = bot.reply_to(message,
                           "Пожалуйста подождите , я ищу ответ😌")
        client = gpt_key()

        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Как дела брат?"}],
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")

        messages = [
            {"role": "user", "content": query},
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
        text = response['choices'][0]['message']['content']
        response_text = text

        # Отправляем ответ обратно в тот же групповой чат

        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            text=response_text)
    elif message.text.startswith('/img'):

        msg = bot.reply_to(message,
                           "Пожалуйста подождите , я создаю картину😌")
        try:
            response = openai.Image.create(
                prompt=message.text,
                model="image-alpha-001",
                size="512x512",
                response_format="b64_json"
            )

            for index, image_dict in enumerate(response["data"]):
                image_data = base64.b64decode(image_dict["b64_json"])
            bot.send_photo(
                chat_id=message.chat.id,
                photo=image_data,
            )
        except:
            bot.send_message(chat_id=message.chat.id, text='Dall-e не может обработать данный запрос')
@bot.message_handler(commands=['start'])
def handle_start(message):

    user_id = message.from_user.id

    result = message.text.split()[-1]
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id FROM referral_system WHERE user_id = %s", (str(user_id),)
    )
    existing_user = cursor.fetchone()
    cursor.execute('''
                        INSERT INTO main_tg_user (telegram_id,name,balance)
                        VALUES (%s,%s,%s)
                        ON CONFLICT DO NOTHING;
                    ''', (user_id,'ChatGPT','5000'))
    conn.commit()

    if str(result) == str("payment"):
        user_id = message.from_user.id
        bot.send_message(user_id,
                         "Каждый твой вопрос тратит токены OpenAI \nТокены это топливо для нейросети \nСтоимость вопроса зависит от его сложности \n1 символ русского языка 1 токен \nЗдесь ты можешь приобрести их под свои потребности\n"
                         "👇Выберите валюту👇", reply_markup=markup18)
    elif result.startswith('img'):
        print(result)
        id = result.replace('img-', '')
        cursor = conn.cursor()
        cursor.execute('SELECT response_image FROM main_midjourney WHERE id = %s', (id,))
        channel_usernames = cursor.fetchone()  # Fetch a single row


        if channel_usernames:
            response_image_url = channel_usernames[0]  # Assuming the response_image URL is in the first column

            response = requests.get(response_image_url)
            if response.status_code == 200:
                bot.send_photo(message.chat.id, photo=response.content)
            else:
                # Handle the case when the image couldn't be fetched
                bot.send_message(message.chat.id, "Failed to fetch the image.")
        else:
            bot.send_message(message.chat.id, "Image not found.")
    else:
        print(result)
        if existing_user:
            pass
        else:
            if user_id == result:
                result = None
                cursor.execute(
                    "INSERT INTO referral_system (user_id, is_referred, invited_by) VALUES (%s, %s, %s)",
                    (str(user_id), True, result)
                )
            else:

                try:
                    int(result)
                    cursor.execute(
                        "INSERT INTO referral_system (user_id, is_referred, invited_by) VALUES (%s, %s, %s)",
                        (str(user_id), True, result)
                    )
                    cursor.execute(
                        "UPDATE main_tg_user SET balance = balance + %s WHERE telegram_id = %s",
                        (3000, result)
                    )
                    bot.send_message(result, f"Поздравляю, вы получили токены за друга {bot.get_chat(user_id).username}")
                except:
                    result = None
                    cursor.execute(
                        "INSERT INTO referral_system (user_id, is_referred, invited_by) VALUES (%s, %s, %s)",
                        (str(user_id), True, result)
                    )

            conn.commit()
        if block(message):
            pass
        elif block2hrs(message):
            pass
        else:
            bot.send_message(user_id, "🤖 Привет, {}! Я бот ChatGPT и DALL-E! Вы можете задавать любые вопросы."
                                          "Бот иногда может грузить ответ "
                                          "в течение нескольких минут. Все зависит от серверов на стороне OpenAI! "
                                          "Советы к правильному использованию:\n\n"
                                          "– Задавайте осмысленные запросы, расписывайте детальнее.\n"
                                          "– Не пишите ерунду иначе одержите её же в ответ.\n\n"
                                          "Примеры вопросов/запросов:\n\n"
                                          "~ Сколько будет 7 * 8?\n"
                                          "~ Когда началась Вторая Мировая?\n"
                                          "~ Напиши код калькулятора на Python\n"
                                          "~ Напиши сочинение как я провел лето\n"
                             "~ /img Милый котик\n\n".format(message.from_user.first_name), reply_markup=markup1)



@bot.message_handler(commands=['admin'])
def admin_command(message):

    user_id = message.from_user.id  # Извлекаем ID пользователя из объекта message
    user_info = bot.get_chat_member(your_channel_username_admin, user_id)
    if user_info.status in ["member", "administrator", "creator"]:
        bot.send_message(user_id, "Вы состоите в группе и можете использовать команду /admin.", reply_markup=admin0)
    else:
        bot.reply_to(message, "Вы не состоите в группе и не можете использовать команду /admin.")


@bot.callback_query_handler(func=lambda call: call.data == "redact_text")
def handle_subscribed_callback(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Выберите куда добавить новый текст", reply_markup=admin7)
@bot.callback_query_handler(func=lambda call: call.data == "Keys")
def handle_subscribed_callback(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Добавить ключ или удалить?", reply_markup=admin9
    )

@bot.callback_query_handler(func=lambda call: call.data == "add_key")
def handle_subscribed_callback(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Введите ключ")
    bot.register_next_step_handler(call.message, add_key)

def add_key(message: Message):
    cur = conn.cursor()

    # Значение для нового ключа
    new_key_value = message.text  # Замените на фактическое значение ключа

    # SQL-запрос INSERT для добавления ключа
    insert_query = "INSERT INTO main_keys (key) VALUES (%s);"
    data_to_insert = (new_key_value,)

    # Выполнение запроса
    cur.execute(insert_query, data_to_insert)

    # Фиксация изменений в базе данных
    conn.commit()

    bot.send_message(message.chat.id,
                     "Ключ успешно сохранен", reply_markup=admin0)
@bot.callback_query_handler(func=lambda call: call.data == "back4")
def handle_subscribed_callback(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Выбирайте", reply_markup=admin0)
@bot.callback_query_handler(func=lambda call: call.data == "back5")
def handle_subscribed_callback(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Реклама каналов", reply_markup=admin)
@bot.callback_query_handler(func=lambda call: call.data == "back7")
def handle_subscribed_callback(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Выберите куда добавить рекламу\nБот должен быть в канале, чтобы он мог проверять подписан ли пользователь, а также в канале должена быть хотя бы одна пригласительная ссылка", reply_markup=admin)
@bot.callback_query_handler(func=lambda call: call.data == "back8")
def handle_subscribed_callback(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Редактирование ценников", reply_markup=admin4)


@bot.callback_query_handler(func=lambda call: call.data == "new_text_rub")
def handle_subscribed_callback(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Введите новый текст")
    bot.register_next_step_handler(call.message, make_rub_text)

def make_rub_text(message: Message):
    try:
        with open('data.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        # Если файла еще нет, создаем пустой словарь
        data = {}

        # Добавляем или обновляем текст для пользователя в словаре
    data['rub'] = ""
    data['rub'] = message.text

    # Сохраняем обновленные данные в JSON файл
    with open('data.json', 'w') as file:
        json.dump(data, file)
    bot.send_message(message.chat.id,
                     "Успешно сохранено",reply_markup=admin0)

@bot.callback_query_handler(func=lambda call: call.data == "new_text_qrypt")
def handle_subscribed_callback(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Введите новый текст")
    bot.register_next_step_handler(call.message, make_qrypt_text)

def make_qrypt_text(message: Message):
    try:
        with open('data.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        # Если файла еще нет, создаем пустой словарь
        data = {}

        # Добавляем или обновляем текст для пользователя в словаре
    data['qript'] = message.text

    # Сохраняем обновленные данные в JSON файл
    with open('data.json', 'w') as file:
        json.dump(data, file)
    bot.send_message(message.chat.id,
                     "Успешно сохранено",reply_markup=admin0)

@bot.callback_query_handler(func=lambda call: call.data == "new_text_qrypt")
def handle_subscribed_callback(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Введите новый текст")

@bot.callback_query_handler(func=lambda call: call.data == "Reklam")
def handle_subscribed_callback(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Реклама каналов", reply_markup=admin)

@bot.callback_query_handler(func=lambda call: call.data == "prices")
def handle_subscribed_callback(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Редактирование ценников", reply_markup=admin4)

@bot.callback_query_handler(func=lambda call: call.data == "new_price")
def handle_subscribed_callback(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Выберите куда добавить новый ценник. Большая просьба не создавать абсолютно идентичных ценников иначе бот при удалении удалит оба", reply_markup=admin6)

@bot.callback_query_handler(func=lambda call: call.data == "no_price")
def handle_subscribed_callback(call):
    user_id = call.from_user.id
    cursor = conn.cursor()
    cursor.execute('SELECT group_type FROM prices')
    promo_chanel_records = cursor.fetchall()
    cursor.execute('SELECT money FROM prices')
    promo_chanel_records1 = cursor.fetchall()
    cursor.execute('SELECT tokens FROM prices')
    promo_chanel_records2 = cursor.fetchall()


    markup = types.InlineKeyboardMarkup(row_width=1)
    for record in range(len(promo_chanel_records)):
        group_code = promo_chanel_records[record][0]
        money = promo_chanel_records1[record][0]
        tokens = promo_chanel_records2[record][0]
        delete_button = types.InlineKeyboardButton(text=f"Тип:{group_code} \nЦена:{money}\nТокены:{tokens}",
                                                   callback_data=f"delete1:{group_code}:{money}:{tokens}")
        markup.add(delete_button)
    btn = types.InlineKeyboardButton("◀️Назад", callback_data="back8")
    markup.add(btn)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Нажмите, что удалить",reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete1:'))
def delete_record_callback(call):
    group_code_to_delete = call.data.split(':')[1]
    money= call.data.split(':')[2]
    tokens = call.data.split(':')[3]
    cursor = conn.cursor()
    cursor.execute('''
            DELETE FROM prices WHERE group_type = %s AND money = %s AND tokens = %s
        ''', (group_code_to_delete, money, tokens))
    conn.commit()

    bot.answer_callback_query(call.id, text=f"Ценник удалён")
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "delete_key")
def handle_subscribed_callback(call):
    user_id = call.from_user.id
    cursor = conn.cursor()
    cursor.execute('SELECT key FROM main_keys')
    keys = cursor.fetchall()


    markup = types.InlineKeyboardMarkup(row_width=1)
    for key in keys:

        delete_button = types.InlineKeyboardButton(
            text=f"Ключ: {key[0]}",
            callback_data=f"delete12:{(key[0])}"
        )
        markup.add(delete_button)

    btn = types.InlineKeyboardButton("◀️Назад", callback_data="back4")
    markup.add(btn)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Выберите ключ для удаления",reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete12:'))
def delete_record_callback(call):
    key = call.data.split(':')[1]

    cursor = conn.cursor()

    cursor.execute('''
                DELETE FROM main_keys WHERE key = %s 
            ''', (key,))
    conn.commit()

    bot.answer_callback_query(call.id, text=f"Ценник удалён")
    bot.delete_message(call.message.chat.id, call.message.message_id)
@bot.callback_query_handler(func=lambda call: call.data == "new_price_rub")
def handle_subscribed_callback(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Введите цену в рублях \nМинимально возможная цена - 60 руб")

    bot.register_next_step_handler(call.message, make_price)

def make_price(message: Message):

    bot.send_message(message.chat.id,
                     "Введите кол-во токенов")
    bot.register_next_step_handler(message, make_price1, message.text)

def make_price1(message, text):
    cursor = conn.cursor()
    cursor.execute('''
            INSERT INTO prices (group_type, money, tokens)
            VALUES (%s, %s, %s)
        ''', ('rub', text, message.text))

    conn.commit()

    bot.send_message(message.chat.id,
                     "Спасибо",
                     reply_markup=admin0)

@bot.callback_query_handler(func=lambda call: call.data == "new_price_qrypt")
def handle_subscribed_callback(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Введите цену в долларах \nМинимально возможная цена - 5$")

    bot.register_next_step_handler(call.message, make_price2)

def make_price2(message: Message):

    bot.send_message(message.chat.id,
                     "Введите кол-во токенов")
    bot.register_next_step_handler(message, make_price22, message.text)

def make_price22(message, text):
    cursor = conn.cursor()
    cursor.execute('''
            INSERT INTO prices (group_type, money, tokens)
            VALUES (%s, %s, %s)
        ''', ('qrypto', text, message.text))

    conn.commit()

    bot.send_message(message.chat.id,
                     "Спасибо",
                     reply_markup=admin0)

@bot.callback_query_handler(func=lambda call: call.data == "subscribed")
def handle_subscribed_callback(call):

    cursor = conn.cursor()
    cursor.execute('SELECT group_code FROM groups WHERE group_type = %s', ('reklam1',))
    channel_usernames = cursor.fetchall()
    user_id = call.from_user.id

    # Переменная для отслеживания, подписан ли пользователь на все каналы группы reklam1
    is_subscribed_to_all = True

    for channel_username in channel_usernames:
        user_info = bot.get_chat_member(channel_username, user_id)
        if user_info.status not in ["member", "administrator", "creator"]:
            is_subscribed_to_all = False
            break

    if is_subscribed_to_all:
        bot.send_message(user_id, "🤖 Привет, {}! Я бот ChatGPT и DALL-E! Вы можете задавать любые вопросы."
                                  "Бот иногда может грузить ответ "
                                  "в течение нескольких минут. Все зависит от серверов на стороне OpenAI! "
                                  "Советы к правильному использованию:\n\n"
                                  "– Задавайте осмысленные запросы, расписывайте детальнее.\n"
                                  "– Не пишите ерунду иначе одержите её же в ответ.\n\n"
                                  "Примеры вопросов/запросов:\n\n"
                                  "~ Сколько будет 7 * 8?\n"
                                  "~ Когда началась Вторая Мировая?\n"
                                  "~ Напиши код калькулятора на Python\n"
                                  "~ Напиши сочинение как я провел лето\n"
                         "~ /img Милый котик\n\n".format(call.from_user.first_name),
                                       reply_markup=markup1)
    else:
        # Если пользователь не подписан на все каналы, отправляем сообщение с просьбой подписаться
        markup = InlineKeyboardMarkup()
        for channel_username in channel_usernames:
            subscribe_button = InlineKeyboardButton(text=str(bot.get_chat(channel_username).title),
                                                    url=str(get_channel_link(channel_username)))  # ccылки на каналы
            markup.add(subscribe_button)
        name = call.from_user.first_name
        subscribe_btn1 = InlineKeyboardButton("✅Подписался", callback_data="subscribed")
        markup.add(subscribe_btn1)
        bot.send_message(user_id, "Доступ к боту временно ограничен", reply_markup=ReplyKeyboardRemove())
        bot.send_message(user_id, f"Хей, {name}, чтобы начать пользоваться ботом необходимо подписаться на наши каналы.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "subscribed1")
def handle_subscribed_callback(call):

    cursor = conn.cursor()
    cursor.execute('SELECT group_code FROM groups WHERE group_type = %s', ('reklam2',))
    channel_usernames = cursor.fetchall()
    user_id = call.from_user.id

    # Переменная для отслеживания, подписан ли пользователь на все каналы группы reklam1
    is_subscribed_to_all = True

    for channel_username in channel_usernames:
        user_info = bot.get_chat_member(channel_username, user_id)
        if user_info.status not in ["member", "administrator", "creator"]:
            is_subscribed_to_all = False
            break

    if is_subscribed_to_all:
        bot.send_message(user_id, "🤖 Привет, {}! Я бот ChatGPT и DALL-E! Вы можете задавать любые вопросы."
                                  "Бот иногда может грузить ответ "
                                  "в течение нескольких минут. Все зависит от серверов на стороне OpenAI! "
                                  "Советы к правильному использованию:\n\n"
                                  "– Задавайте осмысленные запросы, расписывайте детальнее.\n"
                                  "– Не пишите ерунду иначе одержите её же в ответ.\n\n"
                                  "Примеры вопросов/запросов:\n\n"
                                  "~ Сколько будет 7 * 8?\n"
                                  "~ Когда началась Вторая Мировая?\n"
                                  "~ Напиши код калькулятора на Python\n"
                                  "~ Напиши сочинение как я провел лето\n"
                         "~ /img Милый котик\n\n".format(call.from_user.first_name),
                                       reply_markup=markup1)
    else:
        # Если пользователь не подписан на все каналы, отправляем сообщение с просьбой подписаться
        markup = InlineKeyboardMarkup()
        for channel_username in channel_usernames:
            subscribe_button = InlineKeyboardButton(text=str(bot.get_chat(channel_username).title),
                                                    url=str(get_channel_link(channel_username)))  # ccылки на каналы
            markup.add(subscribe_button)

        subscribe_btn1 = InlineKeyboardButton("✅Подписался", callback_data="subscribed1")
        markup.add(subscribe_btn1)
        name = call.from_user.first_name
        bot.send_message(user_id, "Доступ к боту временно ограничен", reply_markup=ReplyKeyboardRemove())
        bot.send_message(user_id, f"Хей, {name}, подпишись на другие наши каналы, чтобы продолжить", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "subscribed2")
def handle_subscribed_callback(call):

    cursor = conn.cursor()
    cursor.execute('SELECT group_code FROM groups WHERE group_type = %s', ('promo_chanel',))
    channel_usernames = cursor.fetchall()
    user_id = call.from_user.id

    # Переменная для отслеживания, подписан ли пользователь на все каналы группы reklam1
    how_many_subs_got = 0

    for channel_username in channel_usernames:
        user_info = bot.get_chat_member(channel_username, user_id)
        if user_info.status in ["member", "administrator", "creator"]:
            how_many_subs_got += 1

    if how_many_subs_got == 0:
        bot.send_message(user_id, "Вы не подписались ни на один канал :(".format(call.from_user.first_name),
                                       reply_markup=markup12)
    else:
        # Если пользователь не подписан на все каналы, отправляем сообщение с просьбой подписаться
        cursor = conn.cursor()
        # Выполняем SQL-запрос для обновления значения поля tokens в таблице Tg_User
        # Суммируем текущее значение tokens с добавляемым количеством tokens_to_add
        cursor.execute("UPDATE main_tg_user SET balance = balance + %s WHERE telegram_id = %s", (3000 * how_many_subs_got, user_id))
        # Подтверждаем изменения в базе данных
        conn.commit()
        name = call.from_user.first_name

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"{name}, поздравляю, вам начислены бонус токены", reply_markup=markup14)

@bot.callback_query_handler(func=lambda call: call.data == "Bonus chanel")
def handle_subscribed_callback(call):
    user_id = call.from_user.id  # Извлекаем ID пользователя из объекта message
    bot.send_message(call.from_user.id, "Выберите куда добавить рекламу\nБот должен быть в канале, чтобы он мог проверять подписан ли пользователь, а также в канале должена быть хотя бы одна пригласительная ссылка",reply_markup=admin2)

@bot.callback_query_handler(func=lambda call: call.data == "delite_chanel")
def handle_subscribed_callback(call):
    user_id = call.from_user.id
    cursor = conn.cursor()
    cursor.execute('SELECT group_code FROM groups')
    promo_chanel_records = cursor.fetchall()


    markup = types.InlineKeyboardMarkup(row_width=1)
    for record in promo_chanel_records:
        group_code = record[0]

        delete_button = types.InlineKeyboardButton(text=f"Удалить {bot.get_chat(group_code).title }", callback_data=f"delete:{group_code}")
        markup.add(delete_button)
    btn = types.InlineKeyboardButton("◀️Назад", callback_data="back5")
    markup.add(btn)
    bot.send_message(user_id, "Список рекламирущихся каналов:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete:'))
def delete_record_callback(call):
    group_code_to_delete = call.data.split(':')[1]
    cursor = conn.cursor()
    cursor.execute('DELETE FROM groups WHERE group_code = %s', (group_code_to_delete,))
    conn.commit()

    bot.answer_callback_query(call.id, text=f"Запись с кодом {group_code_to_delete} удалена")
    bot.delete_message(call.message.chat.id, call.message.message_id)



@bot.callback_query_handler(func=lambda call: call.data == "make_promo")
def handle_subscribed_callback(call):
    bot.send_message(call.from_user.id,
                     "Введите id канала")

    bot.register_next_step_handler(call.message, handle_next_message)

def handle_next_message(message: Message):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO groups (group_code, group_type) VALUES (%s, %s)', (message.text, 'promo_chanel'))
    conn.commit()
    try:
        user_info = bot.get_chat_member(message.text, '6137197109')

    except:
        bot.send_message(message.chat.id,
                         "Бот не является участником канала! Для коректной работы бота, добавьте бота в список участников канала", )
    bot.send_message(message.chat.id, "Спасибо, теперь за подписку на данный канал пользователь сможет получить бонусную валюту", reply_markup=admin)

@bot.callback_query_handler(func=lambda call: call.data == "make_first_block")
def handle_subscribed_callback(call):
    bot.send_message(call.from_user.id,
                     "Введите id канала")
    bot.register_next_step_handler(call.message, handle_next_message1)

def handle_next_message1(message: Message):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO groups (group_code, group_type) VALUES (%s, %s)', (message.text, 'reklam1'))
    conn.commit()
    try:
        user_info = bot.get_chat_member(message.text, '6137197109')

    except:
        bot.send_message(message.chat.id,
                         "Бот не является участником канала! Для коректной работы бота, добавьте бота в список участников канала", )
    bot.send_message(message.chat.id, "Спасибо, теперь при старте работы с ботом пользователь будет обязан подписаться и на этот канал", reply_markup=admin)


@bot.callback_query_handler(func=lambda call: call.data == "make_second_block")
def handle_subscribed_callback(call):
    bot.send_message(call.from_user.id,
                     "Введите id канала")
    bot.register_next_step_handler(call.message, handle_next_message2)


def handle_next_message2(message: Message):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO groups (group_code, group_type) VALUES (%s, %s)', (message.text, 'reklam2'))
    conn.commit()
    try:
        user_info = bot.get_chat_member(message.text, '6137197109')

    except:
        bot.send_message(message.chat.id,
                         "Бот не является участником канала! Для коректной работы бота, добавьте бота в список участников канала", )
    bot.send_message(message.chat.id, "Спасибо, теперь через два часа пользователь будет обязан подписаться и на этот канал", reply_markup=admin)
@bot.callback_query_handler(func=lambda call: call.data == "back")
def handle_subscribed_callback(call):
    user_id = call.from_user.id
    bot.send_message(user_id, "🤖 Привет, {}! Я бот ChatGPT и DALL-E! Вы можете задавать любые вопросы."
                              "Бот иногда может грузить ответ "
                              "в течение нескольких минут. Все зависит от серверов на стороне OpenAI! "
                              "Советы к правильному использованию:\n\n"
                              "– Задавайте осмысленные запросы, расписывайте детальнее.\n"
                              "– Не пишите ерунду иначе одержите её же в ответ.\n\n"
                              "Примеры вопросов/запросов:\n\n"
                              "~ Сколько будет 7 * 8?\n"
                              "~ Когда началась Вторая Мировая?\n"
                              "~ Напиши код калькулятора на Python\n"
                              "~ Напиши сочинение как я провел лето\n"
                     "~ /img Милый котик\n\n".format(call.from_user.first_name),
                     reply_markup=markup1)

@bot.callback_query_handler(func=lambda call: call.data == "back1")
def handle_subscribed_callback(call):
    user_id = call.from_user.id
    user_name = call.from_user.username
    name = call.from_user.first_name

    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM main_tg_user WHERE telegram_id = %s", (user_id,))
    result = str(cursor.fetchone()[0])
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM main_tg_user WHERE telegram_id = %s", (user_id,))
    conn.commit()
    result1 = str(cursor.fetchone()[0])
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) AS count_invites FROM referral_system WHERE invited_by = %s",
        (user_id,)
    )
    result2 = cursor.fetchone()[0]
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"👤 Добро пожаловать, {name}\n"
                     f"├ Ваш юзернейм: {user_name}\n"
                     f"└ Ваш id: {user_id}\n\n"
                     f"👛Баланс токенов: {result}\n\n"
                     f"👥Друзей приглашено: {result2}\n\n"
                     f"🗣Роль: {result1}\n",
                     reply_markup=markup4)

@bot.callback_query_handler(func=lambda call: call.data == "Стендап комик" or call.data == "Журналист" or call.data == "Шеф-повар" or call.data == "Стилист" or call.data == "Математик" or call.data == "Пьяный" or call.data == "Лучший друг" or call.data == "Переводчик" or call.data == "Рассказчик" or call.data == "Мотиватор" or call.data == "Спорщик" or call.data == "Сценарист" or call.data == "Поэт" or call.data == "Философ")
def handle_subscribed_callback(call):
    user_id = call.from_user.id
    user_name = call.from_user.username
    name = call.from_user.first_name

    cursor = conn.cursor()
    cursor.execute("UPDATE main_tg_user SET name = %s WHERE telegram_id = %s;", (call.data, user_id))
    conn.commit()
    cursor.execute("SELECT balance FROM main_tg_user WHERE telegram_id = %s", (user_id,))
    result = str(cursor.fetchone()[0])
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM main_tg_user WHERE telegram_id = %s", (user_id,))
    conn.commit()
    result1 = str(cursor.fetchone()[0])
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) AS count_invites FROM referral_system WHERE invited_by = %s",
        (user_id,)
    )
    result2 = cursor.fetchone()[0]
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"👤 Добро пожаловать, {name}\n"
             f"├ Ваш юзернейм: {user_name}\n"
             f"└ Ваш id: {user_id}\n\n"
             f"👛Баланс токенов: {result}\n\n"
             f"👥Друзей приглашено: {result2}\n\n"
             f"🗣Роль: {result1}\n",
        reply_markup=markup4)



@bot.callback_query_handler(func=lambda call: call.data == "Без роли")
def handle_subscribed_callback(call):
    user_id = call.from_user.id
    user_name = call.from_user.username
    name = call.from_user.first_name

    cursor = conn.cursor()
    cursor.execute("UPDATE main_tg_user SET name = %s WHERE telegram_id = %s;", ('ChatGPT', user_id))
    conn.commit()
    cursor.execute("SELECT balance FROM main_tg_user WHERE telegram_id = %s", (user_id,))
    result = str(cursor.fetchone()[0])
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM main_tg_user WHERE telegram_id = %s", (user_id,))
    conn.commit()
    result1 = str(cursor.fetchone()[0])
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) AS count_invites FROM referral_system WHERE invited_by = %s",
        (user_id,)
    )
    result2 = cursor.fetchone()[0]
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"👤 Добро пожаловать, {name}\n"
             f"├ Ваш юзернейм: {user_name}\n"
             f"└ Ваш id: {user_id}\n\n"
             f"👛Баланс токенов: {result}\n\n"
             f"👥Друзей приглашено: {result2}\n\n"
             f"🗣Роль: {result1}\n",
        reply_markup=markup4)

@bot.callback_query_handler(func=lambda call: call.data == "tokens")
def handle_subscribed_callback(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Каждый твой вопрос тратит токены OpenAI \nТокены это топливо для нейросети \nСтоимость вопроса зависит от его сложности \n1 символ русского языка 1 токен \nЗдесь ты можешь приобрести их под свои потребности\n"
            "👇Выберите валюту👇", reply_markup=markup10)


@bot.callback_query_handler(func=lambda call: call.data == "bonus")
def handle_subscribed_callback(call):
    cursor = conn.cursor()
    cursor.execute('SELECT group_code FROM groups WHERE group_type = %s', ('promo_chanel',))
    channel_usernames = cursor.fetchall()
    user_id = call.from_user.id
    is_subscribed_to_all = True
    for channel_username in channel_usernames:
        user_info = bot.get_chat_member(channel_username, user_id)
        if user_info.status not in ["member", "administrator", "creator"]:
            is_subscribed_to_all = False
            break

    if is_subscribed_to_all:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Ты уже получил все бонусы", reply_markup=markup12)
    else:
        markup = InlineKeyboardMarkup()

        # Если пользователь не подписан на все каналы, отправляем сообщение с просьбой подписаться

        for channel_username in channel_usernames:
            subscribe_button = InlineKeyboardButton(text=str(bot.get_chat(channel_username).title),
                                                    url=str(get_channel_link(channel_username)))  # ccылки на каналы
            markup.add(subscribe_button)
        subscribe_btn1 = InlineKeyboardButton("✅Подписался", callback_data="subscribed2")
        markup.add(subscribe_btn1)


        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Для получения бонус токена 3000, подпишитесь на каналы", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "friend")
def handle_subscribed_callback(call):
    user_id = call.from_user.id
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Приглашайте друзей и получайте за каждого 3000 токенов.\nВаша ссылка для приглашения друзей: \nhttps://t.me/GPT_DALLY_BOT?start={user_id}"
            # "\nАктивных друзей: 0"
            , reply_markup=markup12)

@bot.message_handler(func=lambda message: message.text == '👥Друзья')
def handle_subscribed_callback(message):
    user_id = message.from_user.id
    if block(message):
        pass
    elif block2hrs(message):
        pass
    else:
            bot.send_message(
                user_id,
                f"Приглашайте друзей и получайте за каждого 3000 токенов.\nВаша ссылка для приглашения друзей: \nhttps://t.me/GPT_DALLY_BOT?start={user_id}"
                    , reply_markup=markup14)

@bot.callback_query_handler(func=lambda call: call.data == "role")
def handle_subscribed_callback(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Здесь вы можете выбрать подходящую роль для бота", reply_markup=markup11)
@bot.callback_query_handler(func=lambda call: call.data == "back2")
def handle_subscribed_callback(call):

    user_id = call.from_user.id
    bot.send_message(user_id,
                     "✍️ Здесь ты можешь\n\n"
                     "💸 Купить дополнительные токены, нажав кнопку \"Купить токены\" \n\n"
                     "👥 Пригласить друзей и получить 3000 токенов по кнопке \"Друзья\"\n\n"
                     "🎁 Подписаться на канал спонсора, получив 3000 токенов по кнопке \"Бесплатные токены\"\n\n"
                     "👛 Посмотреть баланс оставшихся токенов по кнопке \"Баланс токенов\"\n\n",
                     reply_markup=markup2)

@bot.callback_query_handler(func=lambda call: call.data == "Crypto")
def handle_subscribed_callback(call):
    cursor = conn.cursor()
    cursor.execute('SELECT money FROM prices WHERE group_type = %s', ("qrypto",))
    channel_usernames = cursor.fetchall()
    cursor.execute('SELECT tokens FROM prices WHERE group_type = %s', ("qrypto",))
    channel_usernames1 = cursor.fetchall()
    markup = InlineKeyboardMarkup()
    for channel_username in range(len(channel_usernames)):
        money = channel_usernames[channel_username][0]
        tokens = channel_usernames1[channel_username][0]
        subscribe_button = InlineKeyboardButton(text=str(channel_usernames[channel_username][0]) + '$',
                                                callback_data=f"delete7:{money}:{tokens}")  # ccылки на каналы
        markup.add(subscribe_button)

    subscribe_btn1 = InlineKeyboardButton("◀️Назад", callback_data="valute")
    markup.add(subscribe_btn1)
    with open('data.json', 'r') as file:
        data = json.load(file)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=data['qript'],
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete7:'))
def delete_record_callback(call):
        money = int(call.data.split(':')[1].replace("🎯", ""))
        tokens = int(call.data.split(':')[2])
        chat_id = call.message.chat.id
        headers = {
            'x-api-key': API_QRIPT,
            'Authorization': 'Bearer ' + generate_jwt_token(),  # Добавляем JWT-токен к заголовку Authorization
        }
        print(chat_id)
        data = {

            'order_id': str(chat_id),  # Уникальный идентификатор заказа, можно использовать chat_id
            'price_amount': int(money),  # Сумма оплаты, обязательный параметр
            'price_currency': 'USD',  # Валюта оплаты, обязательный параметр
            'pay_currency': 'USDTTRC20'  # Валюта для оплаты, обязательный параметр
        }
        response = requests.post('https://api.nowpayments.io/v1/payment', headers=headers, json=data)

        data1 = response.json()


        markup17 = InlineKeyboardMarkup()
        markup17.row(InlineKeyboardButton("🔄Проверить оплату", callback_data=f"check_paymnent:{data1['payment_id']}"))

        subscribe_btn1 = InlineKeyboardButton("◀️Назад", callback_data="valute")
        markup17.add(subscribe_btn1)
        print(data1)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            # f"Оплатите {tokens} токенов. Далее ❗️❗️❗️ОБЯЗАТЕЛЬНО❗❗️❗️️️️️️ нажмите кнопку '🔄Проверить оплату' для подтверждения платежа\nВаш адресс для оплаты: " +
            # data1['pay_address']
            text=f"""
Покупка : {tokens} токенов 
Способ оплаты: USDTTRC20
Сумма оплаты(вместе с комиссией): {data1['pay_amount']} USD


Реквизиты для оплаты👇: 
<code>{data1['pay_address']}</code>

❗️Внимание❗️
Нужно указать точное количество, в противном случае платёж будет отклонен.

Платежи обрабатываются до 5минут, нажмите кнопку "🔄Проверить оплату" спустя 2-3минуты после оплаты.
                    """,
            reply_markup=markup17, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "RUB")
def handle_subscribed_callback(call):
    cursor = conn.cursor()
    cursor.execute('SELECT money FROM prices WHERE group_type = %s', ("rub",))
    channel_usernames = cursor.fetchall()
    cursor.execute('SELECT tokens FROM prices WHERE group_type = %s', ("rub",))
    channel_usernames1 = cursor.fetchall()
    markup = InlineKeyboardMarkup()
    for channel_username in range(len(channel_usernames)):
        money=channel_usernames[channel_username][0]
        tokens=channel_usernames1[channel_username][0]
        subscribe_button = InlineKeyboardButton(text=str(channel_usernames[channel_username][0]) + ' рублей', callback_data= f"delete4:{money}:{tokens}")  # ccылки на каналы
        markup.add(subscribe_button)

    subscribe_btn1 = InlineKeyboardButton("◀️Назад", callback_data="valute")
    markup.add(subscribe_btn1)
    with open('data.json', 'r') as file:
        data = json.load(file)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=data['rub'],
        reply_markup=markup
    )




@bot.callback_query_handler(func=lambda call: call.data.startswith('delete4:'))
def delete_record_callback(call):
        money = int(call.data.split(':')[1].replace("🎯", ""))
        tokens = int(call.data.split(':')[2])
        title = 'Оплата'
        description = f'{tokens} токенов🚀1111 1111 1111 1026, 12/22, CVC 000🎯'
        # Идентификатор для платежа
        invoice_payload = money  # Замените на ваш уникальный идентификатор
        # Провайдерский токен YooKassa
        provider_token = YOOKASSA_SECRET_KEY  # Замените на ваш секретный ключ YooKassa
        # Валюта платежа
        currency = 'RUB'  # Замените на вашу нужную валюту, например, 'RUB' для российских рублей

        price = int(money)*100

        prices = [LabeledPrice(label='Working Time Machine', amount=str(price))]
        bot.send_invoice(
            chat_id=call.from_user.id,
            title=title,
            description=description,
            invoice_payload=invoice_payload,
            provider_token=provider_token,
            currency=currency,
            prices=prices,
        )



@bot.callback_query_handler(func=lambda call: call.data == "recommendations")
def handle_subscribed_callback(call):
    if call.message.text == """Советую прочитать полностью прежде чем начать общаться со мной.

1. Сложные вопросы я рекомендую задавать мне на английском языке, так же на английском языке я работаю быстрее

2. Будьте конкретны и ясны: задавая вопрос, предоставьте как можно больше релевантной информации, чтобы помочь мне лучше понять, что вам нужно.

3. Используйте правильную грамматику и орфографию: так мне будет легче понять ваше сообщение и ответить на него.

4. Будьте вежливы: использование вежливых выражений и проявление уважения могут иметь большое значение для обеспечения позитивного взаимодействия.

5. Избегайте использования аббревиатур или текстовой речи: это может затруднить мне понимание того, что вы пытаетесь донести.

6. Задавайте по одному вопросу за раз: Если у вас есть несколько вопросов, лучше задавать их по одному, чтобы помочь мне дать четкий и целенаправленный ответ.

7. Укажите контекст: Если ваш вопрос связан с определенной темой, предоставьте некоторую справочную информацию, которая поможет мне понять, о чем вы спрашиваете.

8. Избегайте использования всех заглавных букв: ввод текста всеми заглавными буквами часто воспринимается как крик и может затруднить продуктивную беседу.

9. Будьте терпеливы: я являюсь языковой моделью искусственного интеллекта, и мне может понадобиться некоторое время, чтобы обработать ваш запрос. Ответы на некоторые вопросы могут длиться до 2 минут.

10. Для генерации изображений используйте команду /img

Примеры вопросов:
Напиши мне резюме по вакансии финансовый директор.
Сочинение на тему что символизируют горы и море в литературе с примерами из русской литературы.
Напиши рецепт драников.
Отличие булата от дамасской стали.

Пример запроса для генерации изображения:
/img Милый котик

Если ты дочитал до конца - ты молодец, правильно задавая вопросы, я помогу серьезно упростить твою жизнь. Разработчики чат-бота могут это подтвердить
 Жду тебя в чате, мой друг.

Если у вас остались вопросы или есть предложения пишите @AlexVladimirovichB""":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Здесь вы можете посмотреть ответы на распространенные вопросы и проблемы",
            reply_markup=markup3
        )
    else:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="""Советую прочитать полностью прежде чем начать общаться со мной.

1. Сложные вопросы я рекомендую задавать мне на английском языке, так же на английском языке я работаю быстрее

2. Будьте конкретны и ясны: задавая вопрос, предоставьте как можно больше релевантной информации, чтобы помочь мне лучше понять, что вам нужно.

3. Используйте правильную грамматику и орфографию: так мне будет легче понять ваше сообщение и ответить на него.

4. Будьте вежливы: использование вежливых выражений и проявление уважения могут иметь большое значение для обеспечения позитивного взаимодействия.

5. Избегайте использования аббревиатур или текстовой речи: это может затруднить мне понимание того, что вы пытаетесь донести.

6. Задавайте по одному вопросу за раз: Если у вас есть несколько вопросов, лучше задавать их по одному, чтобы помочь мне дать четкий и целенаправленный ответ.

7. Укажите контекст: Если ваш вопрос связан с определенной темой, предоставьте некоторую справочную информацию, которая поможет мне понять, о чем вы спрашиваете.

8. Избегайте использования всех заглавных букв: ввод текста всеми заглавными буквами часто воспринимается как крик и может затруднить продуктивную беседу.

9. Будьте терпеливы: я являюсь языковой моделью искусственного интеллекта, и мне может понадобиться некоторое время, чтобы обработать ваш запрос. Ответы на некоторые вопросы могут длиться до 2 минут.

10. Для генерации изображений используйте команду /img

Примеры вопросов:
Напиши мне резюме по вакансии финансовый директор.
Сочинение на тему что символизируют горы и море в литературе с примерами из русской литературы.
Напиши рецепт драников.
Отличие булата от дамасской стали.

Пример запроса для генерации изображения:
/img Милый котик

Если ты дочитал до конца - ты молодец, правильно задавая вопросы, я помогу серьезно упростить твою жизнь. Разработчики чат-бота могут это подтвердить
 Жду тебя в чате, мой друг.

Если у вас остались вопросы или есть предложения пишите @AlexVladimirovichB""",
            reply_markup=markup3
        )

@bot.callback_query_handler(func=lambda call: call.data == "add_to_group")
def handle_subscribed_callback(call):
    if call.message.text == """Инструкция как общаться с ботом в группе:

1. Добавить бота в группу
2. Добавьте бота в администраторы и выдайте разрешение на общение

3. Используя команду /gpt можно задать ему вопрос.
Например:
/gpt Как дела?

3. Чтобы сгенирировать изображение, используйте команду /img запрос
Например:
/img Картина маслом

Если у вас остались вопросы или есть предложения пишите @AlexVladimirovichB""":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Здесь вы можете посмотреть ответы на распространенные вопросы и проблемы",
            reply_markup=markup3
        )
    else:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="""Инструкция как общаться с ботом в группе:

1. Добавить бота в группу
2. Добавьте бота в администраторы и выдайте разрешение на общение

3. Используя команду /gpt можно задать ему вопрос.
Например:
/gpt Как дела?

3. Чтобы сгенирировать изображение, используйте команду /img запрос
Например:
/img Картина маслом

Если у вас остались вопросы или есть предложения пишите @AlexVladimirovichB""",
            reply_markup=markup3
        )

@bot.callback_query_handler(func=lambda call: call.data == "what_are_tokens")
def handle_subscribed_callback(call):
    if call.message.text == """Токены это топливо для нейросети

Токены тратятся индивидуально. Исходя из расчета вопрос+ответ

1 символ - 1 токен

Одно изображение - 500 токенов

Токены придумали не разработчики бота, а OpenAI

Если у вас остались вопросы или есть предложения пишите @AlexVladimirovichB""":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Здесь вы можете посмотреть ответы на распространенные вопросы и проблемы",
            reply_markup=markup3
        )
    else:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="""Токены это топливо для нейросети

Токены тратятся индивидуально. Исходя из расчета вопрос+ответ

1 символ - 1 токен

Одно изображение - 500 токенов

Токены придумали не разработчики бота, а OpenAI

Если у вас остались вопросы или есть предложения пишите @AlexVladimirovichB""",


            reply_markup=markup3
        )

@bot.callback_query_handler(func=lambda call: call.data == "communication_modes")
def handle_subscribed_callback(call):
    if call.message.text == """В боте есть 14 ролей. Исходя из ваших потребностей вы можете выбрать необходимую для вас

Если у вас остались вопросы или есть предложения пишите @AlexVladimirovichB""":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Здесь вы можете посмотреть ответы на распространенные вопросы и проблемы",
            reply_markup=markup3
        )
    else:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="""В боте есть 14 ролей. Исходя из ваших потребностей вы можете выбрать необходимую для вас

Если у вас остались вопросы или есть предложения пишите @AlexVladimirovichB""",
            reply_markup=markup3
        )

@bot.callback_query_handler(func=lambda call: call.data == "payment_problems")
def handle_subscribed_callback(call):
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Проблемы с оплатой могут возникать по двум причинам:   \n1. Вы не оплатили токены \n2. Вы не нажали кнопку 'Проверить оплату' \nОна находится под ссылкой на оплату, если потеряли - ничего страшного, нажмите кнопку ниже   \nВ иных случаях пишите @AlexVladimirovichB",
            reply_markup=markup13
        )

@bot.callback_query_handler(func=lambda call: call.data == "🔄Юмани токены")
def handle_subscribed_callback(call):
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f'Вы еще не оплатили токены!',
            reply_markup=markup14
        )




@bot.callback_query_handler(func=lambda call: call.data.startswith("check_paymnent:"))
def handle_subscribed_callback(call):
    payment_id = call.data.split(':')[1]
    chat_id = str(call.message.chat.id)

    headers = {
        'x-api-key': API_QRIPT
    }
    payload = {}
    url = f"https://api.nowpayments.io/v1/payment/{payment_id}"
    json_response = requests.request("GET", url, headers=headers, data=payload)
    response = json.loads(json_response.text)

    if response['payment_status'] == 'finished':
        markup17 = InlineKeyboardMarkup()
        markup17.row(InlineKeyboardButton("↩️Вернуться", callback_data="back1"))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="✅Оплата прошла успешно!", reply_markup=markup17)
    else:
        markup17 = InlineKeyboardMarkup()
        markup17.row(InlineKeyboardButton("🔄Проверить оплату", callback_data=f"check_paymnent:{payment_id}"))
        markup17.row(InlineKeyboardButton("↩️Вернуться", callback_data="back1"))
        if call.message.text == "Вы еще не оплатили токены!":
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Вы еще не оплатили токены!!!", reply_markup=markup17)
        else:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Вы еще не оплатили токены!", reply_markup=markup17)

# @bot.callback_query_handler(func=lambda call: call.data == "69р")
# def handle_subscribed_callback(call):
#
#     title = 'Оплата'
#     description = '50000 токенов'
#     # Идентификатор для платежа
#     invoice_payload = '69р'  # Замените на ваш уникальный идентификатор
#     # Провайдерский токен YooKassa
#     provider_token = YOOKASSA_SECRET_KEY  # Замените на ваш секретный ключ YooKassa
#     # Валюта платежа
#     currency = 'RUB'  # Замените на вашу нужную валюту, например, 'RUB' для российских рублей
#     prices = [LabeledPrice(label='Working Time Machine', amount=6900)]
#     bot.send_invoice(
#         chat_id=call.from_user.id,
#         title=title,
#         description=description,
#         invoice_payload=invoice_payload,
#         provider_token=provider_token,
#         currency=currency,
#         prices=prices,
#     )
# @bot.shipping_query_handler(func=lambda query: True)
# def handle_shipping_query(query):
#     # Здесь вы можете обработать варианты доставки, если это необходимо
#     pass
#
# @bot.pre_checkout_query_handler(func=lambda query: True)
# def handle_pre_checkout_query(query):
#     # Вы можете выполнить любые проверки оплаты перед её обработкой
#     bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)
#
#
# @bot.message_handler(content_types=['successful_payment'])
# def handle_successful_payment(message):
#     # Эта функция будет вызвана, когда оплата успешно завершится
#     # Здесь вы можете предоставить пользователю купленные токены или выполнить любые другие действия
#     user_id = message.from_user.id
#     # Получаем информацию о платеже
#     successful_payment = message.successful_payment
#     total_amount = successful_payment.total_amount
#     currency = successful_payment.currency
#     # Отправляем пользователю сообщение о успешной оплате
#     cursor = conn.cursor()
#     # Выполняем SQL-запрос для обновления значения поля tokens в таблице Tg_User
#     # Суммируем текущее значение tokens с добавляемым количеством tokens_to_add
#     cursor.execute("UPDATE main_tg_user SET balance = balance + %s WHERE telegram_id = %s", (50000, user_id))
#     # Подтверждаем изменения в базе данных
#     conn.commit()
#     success_message = f"Поздравляем! Вы успешно оплатили {total_amount / 100} {currency} и получили свои токены."
#     bot.send_message(chat_id=message.chat.id, text=success_message,reply_markup=markup4)

@bot.callback_query_handler(func=lambda call: call.data == "valute")
def handle_subscribed_callback(call):


    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Каждый твой вопрос тратит токены OpenAI \nТокены это топливо для нейросети \nСтоимость вопроса зависит от его сложности \n1 символ русского языка 1 токен \nЗдесь ты можешь приобрести их под свои потребности\n"
                     "👇Выберите валюту👇", reply_markup=markup5)
@bot.callback_query_handler(func=lambda call: call.data == "faq")
def handle_subscribed_callback(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Здесь вы можете посмотреть ответы на распространенные вопросы и проблемы",
                     reply_markup=markup9)
@bot.callback_query_handler(func=lambda call: call.data == "return")
def handle_subscribed_callback(call):

    user_id = call.from_user.id
    bot.send_message(
        user_id,
        "👇🚀Выберите подходящее количество токенов \n"
                     "├ 10.000 токенов за 22руб.\n"
                     "├ 50.000 токенов за 69руб.\n"
                     "🎯120.000 токенов за 139руб. \n"
                     "├ 300.000 токенов за 259руб. \n"
                     '├ 1.000.000 токенов за 699руб. \n'
                     '└ 2.500.000 токенов за 1399руб. \n'
                     '👇Выберите подходящий вариант👇 \n',
        reply_markup=markup6)

@bot.message_handler(func=lambda message: message.text == '♻️Полезное')
def handle_reply(message):
    if block(message):
        pass
    elif block2hrs(message):
        pass
    else:
        user_id = message.from_user.id

        bot.send_message(user_id,
                "✍️ Здесь ты можешь\n\n"
                "💸 Купить дополнительные токены, нажав кнопку \"Купить токены\" \n\n"
                "👥 Пригласить друзей и получить 3000 токенов по кнопке \"Друзья\"\n\n"
                "🎁 Подписаться на канал спонсора, получив 3000 токенов по кнопке \"Бесплатные токены\"\n\n"
                "👛 Посмотреть баланс оставшихся токенов по кнопке \"Баланс токенов\"\n\n",
                         reply_markup=markup2)

@bot.message_handler(func=lambda message: message.text == '👤Профиль')
def handle_reply(message):
    if block(message):
        pass
    elif block2hrs(message):
        pass
    else:
        user_id = message.from_user.id
        user_name = message.from_user.username
        name = message.from_user.first_name

        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM main_tg_user WHERE telegram_id = %s", (user_id,))
        result = str(cursor.fetchone()[0])
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM main_tg_user WHERE telegram_id = %s", (user_id,))
        conn.commit()
        result1 = str(cursor.fetchone()[0])
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) AS count_invites FROM referral_system WHERE invited_by = %s",
            (user_id,)
        )
        result2 = cursor.fetchone()[0]
        bot.send_message(user_id,
                 f"👤 Добро пожаловать, {name}\n"
                 f"├ Ваш юзернейм: {user_name}\n"
                 f"└ Ваш id: {user_id}\n\n"
                 f"👛Баланс токенов: {result}\n\n"
                 f"👥Друзей приглашено: {result2}\n\n"
                 f"🗣Роль: {result1}\n",
            reply_markup=markup4)

@bot.message_handler(func=lambda message: message.text == '◀️Назад')
def handle_reply(message):
    if block(message):
        pass
    elif block2hrs(message):
        pass
    else:
        user_id = message.from_user.id

        bot.send_message(user_id, "🤖 Привет, {}! Я бот ChatGPT и DALL-E! Вы можете задавать любые вопросы."
                                  "Бот иногда может грузить ответ "
                                  "в течение нескольких минут. Все зависит от серверов на стороне OpenAI! "
                                  "Советы к правильному использованию:\n\n"
                                  "– Задавайте осмысленные запросы, расписывайте детальнее.\n"
                                  "– Не пишите ерунду иначе одержите её же в ответ.\n\n"
                                  "Примеры вопросов/запросов:\n\n"
                                  "~ Сколько будет 7 * 8?\n"
                                  "~ Когда началась Вторая Мировая?\n"
                                  "~ Напиши код калькулятора на Python\n"
                                  "~ Напиши сочинение как я провел лето\n"
                         "~ /img Милый котик\n\n".format(message.from_user.first_name),
                         reply_markup=markup1)


@bot.message_handler(func=lambda message: message.text == '👩‍🎓Помощь' or message.text == '❓FAQ')
def handle_reply(message):
    if block(message):
        pass
    elif block2hrs(message):
        pass
    else:
        user_id = message.from_user.id

        bot.send_message(user_id,
                "Здесь вы можете посмотреть ответы на распространенные вопросы и проблемы",
                         reply_markup=markup3)


@bot.message_handler(func=lambda message: message.text == '🎁Бесплатные токены')
def handle_reply(message):
    cursor = conn.cursor()
    cursor.execute('SELECT group_code FROM groups WHERE group_type = %s', ('promo_chanel',))
    channel_usernames = cursor.fetchall()
    user_id = message.from_user.id
    is_subscribed_to_all = True
    for channel_username in channel_usernames:
        user_info = bot.get_chat_member(channel_username, user_id)
        if user_info.status not in ["member", "administrator", "creator"]:
            is_subscribed_to_all = False
            break

    if is_subscribed_to_all:
        bot.send_message(
            user_id,
            "Ты уже получил все бонусы", reply_markup=markup14)
    else:
        markup = InlineKeyboardMarkup()

        # Если пользователь не подписан на все каналы, отправляем сообщение с просьбой подписаться

        for channel_username in channel_usernames:
            subscribe_button = InlineKeyboardButton(text=str(bot.get_chat(channel_username).title),
                                                    url=str(get_channel_link(channel_username)))  # ccылки на каналы
            markup.add(subscribe_button)
        subscribe_btn1 = InlineKeyboardButton("✅Подписался", callback_data="subscribed2")
        markup.add(subscribe_btn1)

        bot.send_message(
            user_id,
            "Для получения бонус токена 3000, подпишитесь на каналы", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '👛Баланс токенов')
def handle_reply(message):
    if block(message):
        pass
    elif block2hrs(message):
        pass
    else:
        user_id = message.from_user.id
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM main_tg_user WHERE telegram_id = %s", (user_id,))
        result = str(cursor.fetchone()[0])

        bot.send_message(user_id,
                "Оставшееся количество токенов: " + result)

@bot.message_handler(func=lambda message: message.text == '🚀Купить токены')
def handle_reply(message):
    if block(message):
        pass
    elif block2hrs(message):
        pass
    else:
        user_id = message.from_user.id

        bot.send_message(user_id,
                "Каждый твой запрос тратит токены OpenAI \nТокены это топливо для нейросети \nСтоимость вопроса зависит от его сложности \n1 символ русского языка 1 токен \nЗдесь ты можешь приобрести их под свои потребности\n"
                "👇Выберите валюту👇", reply_markup=markup18)




@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout_query(query):
    bot.answer_pre_checkout_query(query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):
    # Эта функция будет вызвана, когда оплата успешно завершится
    # Здесь вы можете предоставить пользователю купленные токены или выполнить любые другие действия
    user_id = message.from_user.id
    # Получаем информацию о платеже
    amount_paid = int(message.successful_payment.total_amount)



    # Отправляем пользователю сообщение о успешной оплате
    cursor = conn.cursor()

    if int(amount_paid) == 25900:
        amount_paid = "🎯259"
    else:
        amount_paid = int(amount_paid) // 100
    query = "SELECT tokens FROM prices WHERE money = %s AND group_type = %s"
    cursor.execute(query, (str(amount_paid), 'rub'))
    result = cursor.fetchone()
    # Выполняем SQL-запрос для обновления значения поля tokens в таблице Tg_User
    # Суммируем текущее значение tokens с добавляемым количеством tokens_to_add
    #tokens
    cursor.execute("UPDATE main_tg_user SET balance = balance + %s WHERE telegram_id = %s", (int(result[0]), user_id))
    # Подтверждаем изменения в базе данных
    conn.commit()
    success_message = f"Поздравляем! Вы успешно заплатили {amount_paid} рублей и получили свои {result[0]} токенов."
    bot.send_message(chat_id=message.chat.id, text=success_message, reply_markup=markup4)


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    if message.text.startswith('/img'):
        if block(message):
            pass
        elif block2hrs(message):
            pass
        else:
            msg = bot.reply_to(message,
                               "Пожалуйста подождите , я создаю картину😌")
            client = gpt_key()

            cursor = conn.cursor()
            query = "SELECT balance FROM main_tg_user WHERE telegram_id = %s;"
            cursor.execute(query, (message.from_user.id,))

            # Получаем результат запроса
            result = cursor.fetchone()[0]
            if int(result) < 500:
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=msg.message_id,
                    text="Вы исчерпали все свои токены   \nНе забывай приглашать друзей по реферальной ссылке, чтобы получить токены прямо сейчас 👇",
                    reply_markup=markup16)
            else:
                update_tokens_query = "UPDATE main_tg_user SET balance = balance - %s WHERE telegram_id = %s;"
                cursor.execute(update_tokens_query, (500, str(message.from_user.id)))
                # Обязательно выполните коммит, чтобы сохранить изменения в базе данных
                conn.commit()
                try:
                    response = client.images.generate(
                        model="dall-e-2",
                        prompt=message.text,
                        size="256x256",
                        quality="standard",
                        n=1,
                    )

                    image_url = response.data[0].url

                    bot.send_photo(
                        chat_id=message.chat.id,
                        photo=image_url,
                    )
                except:
                    bot.send_message(chat_id=message.chat.id, text='Dall-e не может обработать данный запрос')
    elif message.text.startswith('/gpt') or message.chat.type == 'private':
        if block(message):
            pass
        elif block2hrs(message):
            pass
        else:
            print(message.chat.type)
            client = gpt_key()
            chat_id = message.chat.id
            message.text = message.text.replace('/gpt','')
            msg = bot.reply_to(message,
                             "Пожалуйста подождите , я ищу ответ😌")
            cursor = conn.cursor()


            role = "SELECT name FROM main_tg_user WHERE telegram_id = %s;"
            cursor.execute(role, (str(message.from_user.id),))
            role = cursor.fetchone()



            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                {"role": "system", "content": f"Веди себя как {role}"},
                {"role": "user", "content": message.text},
            ],
                stream=True,
            )
            text = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    text = text + chunk.choices[0].delta.content









            query = "SELECT balance FROM main_tg_user WHERE telegram_id = %s;"
            cursor.execute(query, (message.from_user.id,))

            # Получаем результат запроса
            result = cursor.fetchone()[0]
            if int(result) < len(text):
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=msg.message_id,
                    text="Вы исчерпали все свои токены   \nНе забывай приглашать друзей по реферальной ссылке, чтобы получить токены прямо сейчас 👇", reply_markup=markup16)

            else:
                update_tokens_query = "UPDATE main_tg_user SET balance = balance - %s WHERE telegram_id = %s;"
                cursor.execute(update_tokens_query, (str(len(text)), str(message.from_user.id)))
                # Обязательно выполните коммит, чтобы сохранить изменения в базе данных
                conn.commit()
                response_text = text

                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=msg.message_id,
                    text=response_text)


# def main():
#     while True:
#         try:
#             bot.polling(none_stop=True)  # Параметр none_stop=True позволяет автоматически перезапускать бота при ошибке
#         except Exception as e:
#             print(f"Ошибка: {e}")
#             # Ожидание некоторого времени перед следующей попыткой перезапуска (необязательно)
#             time.sleep(5)  # Подождать 5 секунд перед следующей попыткой
#
# if __name__ == '__main__':
#     main()
bot.polling(none_stop=True)  # Параметр none_stop=True позволяет автоматически перезапускать бота при ошибке
