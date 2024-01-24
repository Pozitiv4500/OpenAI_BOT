from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import *
markup1 = ReplyKeyboardMarkup(resize_keyboard=True)


profile_btn = KeyboardButton("👤Профиль")
help_btn = KeyboardButton("👩‍🎓Помощь")
useful_btn = KeyboardButton("♻️Полезное")

markup1.row(profile_btn,help_btn)
markup1.row(useful_btn)


markup2 = ReplyKeyboardMarkup(resize_keyboard=True)
buy_tokens_btn1 = KeyboardButton("🚀Купить токены")
free_tokens_btn1 = KeyboardButton("🎁Бесплатные токены")
free_tokens_btn2 = KeyboardButton("👥Друзья")
balance_btn = KeyboardButton("👛Баланс токенов")
back_btn = KeyboardButton("◀️Назад")
markup2.row(buy_tokens_btn1)
markup2.row(free_tokens_btn1,free_tokens_btn2)
markup2.row(balance_btn)
markup2.row(back_btn)


markup = InlineKeyboardMarkup()
subscribe_btn1 = types.InlineKeyboardButton("✅Подписался", callback_data="subscribed")
markup.add(subscribe_btn1)
back = InlineKeyboardButton("◀️Назад", callback_data="back")

markup3 = InlineKeyboardMarkup()
markup3.row(InlineKeyboardButton("❗️Рекомендации", callback_data="recommendations"))
markup3.row(InlineKeyboardButton("➕Добавить бота в группу", callback_data="add_to_group"),)
markup3.row(InlineKeyboardButton("❓Что такое токены?", callback_data="what_are_tokens"))
markup3.row(InlineKeyboardButton("👩‍🎓О режимах общения", callback_data="communication_modes"),)
markup3.row(InlineKeyboardButton("🚨Проблемы с оплатой", callback_data="payment_problems"))
markup3.row(back)

markup4 = InlineKeyboardMarkup()
markup4.row(InlineKeyboardButton("🚀Купить токены", callback_data="tokens"))
markup4.row(InlineKeyboardButton("🎁Бонус токены", callback_data="bonus"),InlineKeyboardButton("👥Привести друга", callback_data="friend"))
markup4.row(InlineKeyboardButton("🧠Роль", callback_data="role"))
markup4.row(InlineKeyboardButton("❓FAQ", callback_data="faq"),InlineKeyboardButton("🤝Помощь", url='https://t.me/AlexVladimirovichB'))
markup4.row(back)

back1 = InlineKeyboardButton("◀️Назад", callback_data="back1")

markup5 = InlineKeyboardMarkup()
markup5.row(InlineKeyboardButton("RUB", callback_data="RUB"),InlineKeyboardButton("Crypto(+5%)", callback_data="Crypto"))
markup5.row(InlineKeyboardButton("◀️Назад", callback_data="back2"))

value = InlineKeyboardButton("↩️Вернуться к выбору валюты", callback_data="valute")
markup6 = InlineKeyboardMarkup()
markup6.row(InlineKeyboardButton("22р", callback_data="22р"),InlineKeyboardButton("69р", callback_data="69р"))
markup6.row(InlineKeyboardButton("🎯139р", callback_data="🎯139р"),InlineKeyboardButton("259р", callback_data="259р"))
markup6.row(InlineKeyboardButton("699р", callback_data="699р"),InlineKeyboardButton("1399р", callback_data="1399р"))
markup6.row(value)


markup7 = InlineKeyboardMarkup()
markup7.row(InlineKeyboardButton("2$", callback_data="2$"),InlineKeyboardButton("5$", callback_data="5$"))
markup7.row(InlineKeyboardButton("🎯10$", callback_data="🎯10$"),InlineKeyboardButton("20$", callback_data="20$"))
markup7.row(InlineKeyboardButton("50$", callback_data="50$"),InlineKeyboardButton("100$", callback_data="100$"))
markup7.row(value)

markup8 = InlineKeyboardMarkup()
markup8.row(InlineKeyboardButton("↩️Вернуться", callback_data="return"))



markup9 = InlineKeyboardMarkup()

markup9.row(InlineKeyboardButton("❗️Рекомендации", callback_data="recommendations"))
markup9.row(InlineKeyboardButton("➕Добавить бота в группу", callback_data="add_to_group"),)
markup9.row(InlineKeyboardButton("❓Что такое токены?", callback_data="what_are_tokens"))
markup9.row(InlineKeyboardButton("👩‍🎓О режимах общения", callback_data="communication_modes"),)
markup9.row(InlineKeyboardButton("🚨Проблемы с оплатой", callback_data="payment_problems"))
markup9.row(back1)

markup10 = InlineKeyboardMarkup()
markup10.row(InlineKeyboardButton("RUB", callback_data="RUB"),InlineKeyboardButton("Crypto(+5%)", callback_data="Crypto"))
markup10.row(InlineKeyboardButton("◀️Назад", callback_data="back1"))

markup11 = InlineKeyboardMarkup()

markup11.row(InlineKeyboardButton("Журналист", callback_data="Журналист"),InlineKeyboardButton("Шеф-повар", callback_data="Шеф-повар"))
markup11.row(InlineKeyboardButton("Стилист", callback_data="Стилист"),InlineKeyboardButton("Математик", callback_data="Математик"))
markup11.row(InlineKeyboardButton("Лучший друг", callback_data="Лучший друг"),InlineKeyboardButton("ChatGPT", callback_data="Без роли"))
markup11.row(InlineKeyboardButton("Переводчик", callback_data="Переводчик"),InlineKeyboardButton("Рассказчик", callback_data="Рассказчик"))
markup11.row(InlineKeyboardButton("Мотиватор", callback_data="Мотиватор"),InlineKeyboardButton("Спорщик", callback_data="Спорщик"))
markup11.row(InlineKeyboardButton("Сценарист", callback_data="Сценарист"),InlineKeyboardButton("Поэт", callback_data="Поэт"))
markup11.row(InlineKeyboardButton("Философ", callback_data="Философ"),InlineKeyboardButton("Стендап комик", callback_data="Стендап комик"))
markup11.row(InlineKeyboardButton("◀️Назад", callback_data="back1"))

markup12 = InlineKeyboardMarkup()
markup12.row(InlineKeyboardButton("◀️Назад", callback_data="back1"))

admin0 = InlineKeyboardMarkup()
admin0.row(InlineKeyboardButton("Реклама", callback_data="Reklam"),InlineKeyboardButton("Ценники", callback_data="prices"))
admin0.row(InlineKeyboardButton("Ключи", callback_data="Keys"))
admin0.row(InlineKeyboardButton("◀️Назад", callback_data="back1"))

admin9 = InlineKeyboardMarkup()
admin9.row(InlineKeyboardButton("Добавить ключ", callback_data="add_key"),InlineKeyboardButton("Удалить ключ", callback_data="delete_key"))

admin9.row(InlineKeyboardButton("◀️Назад", callback_data="back1"))
#,InlineKeyboardButton("Добавить новый ценник", callback_data="new_price") ,InlineKeyboardButton("Удалить ценник", callback_data="del_price")
admin = InlineKeyboardMarkup()
admin.row(InlineKeyboardButton("Добавить новый канал для рекламы", callback_data="Bonus chanel"))
admin.row(InlineKeyboardButton("Удалить канал для рекламы", callback_data="delite_chanel"))
admin.row(InlineKeyboardButton("◀️Назад", callback_data="back4"))

admin4 = InlineKeyboardMarkup()
admin4.row(InlineKeyboardButton("Редактировать текст ценника", callback_data="redact_text"))
admin4.row(InlineKeyboardButton("Добавить новый ценник", callback_data="new_price"))
admin4.row(InlineKeyboardButton("Удалить ценник", callback_data="no_price"))
admin4.row(InlineKeyboardButton("◀️Назад", callback_data="back4"))

markup13 = InlineKeyboardMarkup()
markup13.row(InlineKeyboardButton("🔄Проверить оплату", callback_data="🔄Юмани токены"))
markup13.row(InlineKeyboardButton("🤝Помощь", url='https://t.me/AlexVladimirovichB'))

markup14 = InlineKeyboardMarkup()
markup14.row(InlineKeyboardButton("◀️Назад", callback_data="back"))

admin2 = InlineKeyboardMarkup()
admin2.row(InlineKeyboardButton("Промо каналы", callback_data="make_promo"))
admin2.row(InlineKeyboardButton("Каналы блокирующие использование при первом входе", callback_data="make_first_block"))
admin2.row(InlineKeyboardButton("Каналы блокирующие использование через пару часов использования", callback_data="make_second_block"))
admin2.row(InlineKeyboardButton("◀️Назад", callback_data="back5"))

markup16 = InlineKeyboardMarkup()
markup16.row(InlineKeyboardButton("🎁Бонус токены", callback_data="bonus"))
markup16.row(InlineKeyboardButton("👥Реферальная система", callback_data="friend"))
markup16.row(InlineKeyboardButton("🚀Купить токены", callback_data="tokens"))

admin6 = InlineKeyboardMarkup()
admin6.row(InlineKeyboardButton("RUB", callback_data="new_price_rub"))
admin6.row(InlineKeyboardButton("qript", callback_data="new_price_qrypt"))


admin7 = InlineKeyboardMarkup()
admin7.row(InlineKeyboardButton("RUB", callback_data="new_text_rub"))
admin7.row(InlineKeyboardButton("qript", callback_data="new_text_qrypt"))

markup18 = InlineKeyboardMarkup()
markup18.row(InlineKeyboardButton("RUB", callback_data="RUB"),InlineKeyboardButton("Crypto(+5%)", callback_data="Crypto"))
markup18.row(InlineKeyboardButton("◀️Назад", callback_data="back2"))


