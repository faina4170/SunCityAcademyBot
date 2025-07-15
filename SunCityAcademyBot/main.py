import os
import telebot
from telebot import types
import re
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Загружаем переменные окружения из .env файла
load_dotenv()

# Инициализация бота с токеном из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
MANAGER_CHAT_ID = int(os.getenv('MANAGER_CHAT_ID'))

if not BOT_TOKEN or not MANAGER_CHAT_ID:
    raise ValueError("Не удалось загрузить BOT_TOKEN или MANAGER_CHAT_ID из .env файла")

bot = telebot.TeleBot(BOT_TOKEN)

# Хранилище данных пользователей
user_data = {}

class User:
    def __init__(self):
        self.user_type = None
        self.age = None
        self.interest = None
        self.name = None
        self.phone = None
        self.email = None
        self.selected_course = None


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    user_data[user_id] = User()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Для ребёнка')
    btn2 = types.KeyboardButton('Для взрослого')
    btn3 = types.KeyboardButton('Я педагог')
    markup.add(btn1, btn2, btn3)

    bot.send_message(
        user_id,
        "Здравствуйте! 👋 Я помогу вам подобрать курс в Академии Сан Сити.\n\n"
        "Уточните, пожалуйста, для кого вы подбираете обучение:",
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text in ['Для ребёнка', 'Для взрослого', 'Я педагог'])
def handle_user_type(message):
    user_id = message.chat.id
    if user_id not in user_data:
        user_data[user_id] = User()
    user_data[user_id].user_type = message.text

    if message.text == 'Для ребёнка':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('5-6 лет')
        btn2 = types.KeyboardButton('7-9 лет')
        btn3 = types.KeyboardButton('10-12 лет')
        btn4 = types.KeyboardButton('13-15 лет')
        markup.add(btn1, btn2, btn3, btn4)

        bot.send_message(
            user_id,
            "Сколько лет вашему ребёнку?",
            reply_markup=markup
        )
    else:
        ask_for_interests(user_id)


def ask_for_interests(user_id):
    user = user_data[user_id]

    if user.user_type == 'Для взрослого':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Курсы личностного роста')
        btn2 = types.KeyboardButton('Улучшение когнитивных навыков')
        btn3 = types.KeyboardButton('Память и внимание')
        btn4 = types.KeyboardButton('Работа со стрессом')
        btn5 = types.KeyboardButton('Другое')
        markup.add(btn1, btn2, btn3, btn4, btn5)

        bot.send_message(
            user_id,
            "Подскажите, какие направления вас интересуют:",
            reply_markup=markup
        )
    elif user.user_type == 'Я педагог':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = [
            'Курсы повышения квалификации',
            'Курсы профессиональной переподготовки',
            'Обучение нейропедагогике',
            'Обучение нейропсихологии',
            'Обучение скорочтению',
            'Обучение ментальной арифметике',
            'Авторские методические пособия',
            'Обучение мнемотехникам',
            'Работа с трудностями письма',
            'Другое'
        ]
        markup.add(*[types.KeyboardButton(btn) for btn in buttons])

        bot.send_message(
            user_id,
            "Какое направление вас интересует?",
            reply_markup=markup
        )


@bot.message_handler(func=lambda message: user_data.get(message.chat.id) and
                                          user_data[message.chat.id].user_type == 'Для ребёнка' and
                                          user_data[message.chat.id].age is None)
def handle_child_age(message):
    user_id = message.chat.id
    user_data[user_id].age = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    courses = [
        'Нейроподготовка к школе',
        'Развитие внимания, памяти, мышления',
        'Скорочтение',
        'Математика',
        'Эмоциональный интеллект',
        'Подготовка к 1 классу',
        'Другое'
    ]
    markup.add(*[types.KeyboardButton(course) for course in courses])

    bot.send_message(
        user_id,
        "Какие программы вас интересуют?",
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: user_data.get(message.chat.id) and
                                          user_data[message.chat.id].interest is None and
                                          (user_data[message.chat.id].user_type in ['Для взрослого', 'Я педагог'] or
                                           user_data[message.chat.id].age is not None))
def handle_interests(message):
    user_id = message.chat.id
    user_data[user_id].interest = message.text
    ask_for_contacts(user_id)


def ask_for_contacts(user_id):
    bot.send_message(
        user_id,
        "Отлично! Теперь укажите ваши контактные данные.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.send_message(
        user_id,
        "Пожалуйста, введите ваше имя:"
    )


@bot.message_handler(func=lambda message: user_data.get(message.chat.id) and
                                          user_data[message.chat.id].name is None and
                                          user_data[message.chat.id].interest is not None)
def handle_name(message):
    user_id = message.chat.id
    user_data[user_id].name = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_contact = types.KeyboardButton("Отправить номер автоматически", request_contact=True)
    btn_manual = types.KeyboardButton("Ввести номер вручную")
    markup.add(btn_contact, btn_manual)

    bot.send_message(
        user_id,
        "Спасибо! Теперь укажите ваш номер телефона.\n"
        "Вы можете:\n"
        "1. Нажать кнопку 'Отправить номер автоматически'\n"
        "2. Или ввести номер вручную (в формате +79998887766 или 89998887766)",
        reply_markup=markup
    )


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    if message.contact is not None:
        user_id = message.chat.id
        user_data[user_id].phone = message.contact.phone_number
        ask_for_email(user_id)


@bot.message_handler(func=lambda message: user_data.get(message.chat.id) and
                                          user_data[message.chat.id].name is not None and
                                          user_data[message.chat.id].phone is None)
def handle_phone_input(message):
    user_id = message.chat.id

    if message.text == "Ввести номер вручную":
        bot.send_message(
            user_id,
            "Введите номер телефона в формате:\n+79998887766 или 89998887766",
            reply_markup=types.ReplyKeyboardRemove()
        )
        return

    phone = message.text
    if re.match(r'^(\+7|8)\d{10}$', phone):
        user_data[user_id].phone = phone
        ask_for_email(user_id)
    else:
        bot.send_message(
            user_id,
            "⚠️ Некорректный формат номера. Пожалуйста, введите номер в формате:\n"
            "+79998887766 или 89998887766 (11 цифр после +7/8)"
        )


def ask_for_email(user_id):
    bot.send_message(
        user_id,
        "Отлично! Теперь введите ваш email:",
        reply_markup=types.ReplyKeyboardRemove()
    )


@bot.message_handler(func=lambda message: user_data.get(message.chat.id) and
                                          user_data[message.chat.id].phone is not None and
                                          user_data[message.chat.id].email is None)
def handle_email(message):
    user_id = message.chat.id
    email = message.text

    if '@' in email and '.' in email:
        user_data[user_id].email = email

        # Выбор конкретной программы
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if user_data[user_id].user_type == 'Для ребёнка':
            programs = [
                'Нейроподготовка к школе',
                'Скорочтение',
                'Ментальная арифметика',
                'Эмоциональный интеллект'
            ]
        elif user_data[user_id].user_type == 'Для взрослого':
            programs = [
                'Курс личностного роста',
                'Тренировка памяти',
                'Управление стрессом '
            ]
        else:  # Для педагогов
            programs = [
                'Курс повышения квалификации',
                'Нейропедагогика',
                'Методика скорочтения'
            ]

        markup.add(*[types.KeyboardButton(program) for program in programs])

        bot.send_message(
            user_id,
            "Пожалуйста, выберите конкретную программу:",
            reply_markup=markup
        )
    else:
        bot.send_message(
            user_id,
            "⚠️ Пожалуйста, введите корректный email (например, example@mail.ru)"
        )


@bot.message_handler(func=lambda message: user_data.get(message.chat.id) and
                                      user_data[message.chat.id].email is not None and
                                      user_data[message.chat.id].selected_course is None)
def handle_course_selection(message):
    user_id = message.chat.id
    user_data[user_id].selected_course = message.text

    user = user_data[user_id]
    manager_message = (
        "📌 Новая заявка на курс:\n\n"
        f"Тип: {user.user_type}\n"
        f"Программа: {user.selected_course}\n"
        f"Имя: {user.name}\n"
        f"Телефон: {user.phone}\n"
        f"Email: {user.email}"
    )

    if user.user_type == 'Для ребёнка':
        manager_message += f"\nВозраст ребёнка: {user.age}"

    try:
        bot.send_message(MANAGER_CHAT_ID, manager_message)
        bot.send_message(
            user_id,
            f"✅ Спасибо за выбор программы {user.selected_course}!\n"
            "Наш менеджер свяжется с вами в ближайшее время для уточнения деталей.",
            reply_markup=types.ReplyKeyboardRemove()
        )
    except Exception as e:
        print(f"Ошибка отправки менеджеру: {e}")
        bot.send_message(
            user_id,
            "✅ Ваши данные получены! Приносим извинения, возникли технические сложности. "
            "Менеджер обязательно свяжется с вами.",
            reply_markup=types.ReplyKeyboardRemove()
        )


app = Flask(__name__)


# Keep-alive handler
@app.route('/ping')
def ping():
    return "pong"


@app.route('/')
def home():
    return "Бот работает!"


def run_flask():
    try:
        # Try to get Replit-specific info (will work only on Replit)
        repl_slug = os.environ.get('REPL_SLUG', 'not-on-replit')
        repl_owner = os.environ.get('REPL_OWNER', 'not-on-replit')
        if repl_slug != 'not-on-replit' and repl_owner != 'not-on-replit':
            print(f"Публичный URL: https://{repl_slug}.{repl_owner}.replit.dev")
        else:
            print("Сервер запущен локально")
    except Exception as e:
        print(f"Ошибка при получении информации о Replit: {e}")

    app.run(host='0.0.0.0', port=8080)


Thread(target=run_flask).start()
bot.polling(none_stop=True)


