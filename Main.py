import json
import os

import threading
import time
from datetime import datetime

import telebot
from telebot import types

from Profile import FitnessCoefficient
from Workouts import ExerciseCalculator

bot = telebot.TeleBot("8438729431:AAEZdOQT7de43BWCmDYCVNoeckb4oiIWHTI")
waiting_for_input = ""

@bot.message_handler(commands=['start'])
def start(message):
  welcome = f"""{message.from_user.first_name}, Привет!
  Меня зовут Арнольд🦍, я тебя приобщу к ЗОЖ (здоровому образу жизни).
  Вноси свои физические данные в разделе "Изменить профиль" и выбирай тренировку по душе!
  Открой /menu, что бы ознакомиться с функционалом.
    """
  bot.send_message(message.chat.id, welcome)


@bot.message_handler(commands=['menu'])
def menu(message):
    markup = types.InlineKeyboardMarkup()
    button_profile = types.InlineKeyboardButton(text='Профиль🪪', callback_data='profile')
    markup.add(button_profile)
    button_edit_profile = types.InlineKeyboardButton(text='Изменить профиль⚙️', callback_data='edit_profile')
    markup.add(button_edit_profile)
    button_workout = types.InlineKeyboardButton(text='Готовые тренировки✅', callback_data='workout')
    markup.add(button_workout)
    button_notes = types.InlineKeyboardButton(text='Личная тренировка📃', callback_data='notes')
    markup.add(button_notes)
    button_reminder = types.InlineKeyboardButton(text='Установить напоминание📆', callback_data='reminder')
    markup.add(button_reminder)
    button_exercises = types.InlineKeyboardButton(text='Сборник упражнений📕', callback_data='exercises')
    markup.add(button_exercises)
    bot.send_message(message.chat.id, text='――――🦾Все функции бота!🗂――――', reply_markup=markup, parse_mode='html')



# Файл для хранения заметок
NOTES_FILE = "notes.json"


# Загружаем заметки из файла
def load_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Конвертируем ключи заметок в int
            for user_id in data:
                data[user_id] = {int(k): v for k, v in data[user_id].items()}
            return data
    return {}


# Сохраняем заметки в файл
def save_notes(notes):
    with open(NOTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


# Пересоздаем заметки с правильной нумерацией
def renumber_notes(user_notes):
    if not user_notes:
        return {}

    # Сортируем по старым ID и создаем новые по порядку
    sorted_notes = sorted(user_notes.items())
    return {i + 1: note_text for i, (old_id, note_text) in enumerate(sorted_notes)}


# Команда /add - добавить заметку
@bot.message_handler(commands=['add'])
def add_note(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "📝 Напиши название упражнения и количество упражнений в каждом из подходов:")
    bot.register_next_step_handler(msg, process_note)


def process_note(message):
    chat_id = message.chat.id
    note_text = message.text

    notes = load_notes()

    # Создаем ID для заметки
    if str(chat_id) not in notes:
        notes[str(chat_id)] = {}

    note_id = len(notes[str(chat_id)]) + 1
    notes[str(chat_id)][note_id] = note_text

    save_notes(notes)
    bot.send_message(chat_id, f"✅ Упражнение #{note_id} сохранено!")


# Команда /list - показать все заметки
@bot.message_handler(commands=['list'])
def list_notes(message):
    chat_id = message.chat.id
    notes = load_notes()

    user_notes = notes.get(str(chat_id), {})

    if not user_notes:
        bot.send_message(chat_id, "📭 У тебя пока нет упражнений")
        return

    response = "📋 Твои упражнения:\n\n"
    for note_id, note_text in user_notes.items():
        response += f"#{note_id}: {note_text}\n\n"

    bot.send_message(chat_id, response)


# Команда /delete - удалить заметку
@bot.message_handler(commands=['delete'])
def delete_note(message):
    chat_id = message.chat.id
    notes = load_notes()

    user_notes = notes.get(str(chat_id), {})

    if not user_notes:
        bot.send_message(chat_id, "📭 Нечего удалять - упражнений нет")
        return

    # Показываем список заметок для удаления
    response = "❌ Какое упражнение удалить? Напиши номер:\n\n"
    for note_id, note_text in user_notes.items():
        response += f"#{note_id}: {note_text}\n"

    msg = bot.send_message(chat_id, response)
    bot.register_next_step_handler(msg, process_delete_note)


def process_delete_note(message):
    chat_id = message.chat.id
    try:
        note_id = int(message.text)
        notes = load_notes()

        user_notes = notes.get(str(chat_id), {})

        if note_id in user_notes:
            # Удаляем заметку
            del notes[str(chat_id)][note_id]

            # Перенумеровываем оставшиеся заметки
            notes[str(chat_id)] = renumber_notes(notes[str(chat_id)])

            save_notes(notes)
            bot.send_message(chat_id, f"✅ Упражнение #{note_id} удалено!")
        else:
            bot.send_message(chat_id, f"⚠️ ЗУпражнение #{note_id} не найдено")

    except ValueError:
        bot.send_message(chat_id, "❌ Напиши номер Упражнения цифрой")


# Команда /clear - очистить все заметки
@bot.message_handler(commands=['clear'])
def clear_notes(message):
    chat_id = message.chat.id
    notes = load_notes()

    if str(chat_id) in notes and notes[str(chat_id)]:
        notes[str(chat_id)] = {}
        save_notes(notes)
        bot.send_message(chat_id, "🗑️ Все упражнения удалены!")
    else:
        bot.send_message(chat_id, "📭 Нечего удалять - упражнений нет")


# Простое хранилище в памяти
user_reminders = {}


@bot.message_handler(commands=['set'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('➕ Добавить', '📋 Список', '❌ Удалить')
    bot.send_message(message.chat.id, "Привет! Я напомню нужные тебе события!", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == '➕ Добавить')
def add_reminder(message):
    msg = bot.send_message(message.chat.id, "Введите день и время в формате:\n'понедельник 14:30 Напоминание'")
    bot.register_next_step_handler(msg, process_reminder)


def process_reminder(message):
    try:
        parts = message.text.split(' ', 2)
        day = parts[0].lower()
        time_str = parts[1]
        text = parts[2]

        # Проверяем день
        days = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
        if day not in days:
            bot.send_message(message.chat.id, "Ошибка в дне недели!")
            return

        # Проверяем время
        datetime.strptime(time_str, '%H:%M')

        # Сохраняем
        if message.chat.id not in user_reminders:
            user_reminders[message.chat.id] = []

        user_reminders[message.chat.id].append({
            'day': day,
            'time': time_str,
            'text': text
        })

        bot.send_message(message.chat.id, f"✅ Добавлено: {day} в {time_str}")

    except:
        bot.send_message(message.chat.id, "Ошибка формата! Используйте: 'понедельник 14:30 Текст'")


@bot.message_handler(func=lambda m: m.text == '📋 Список')
def list_reminders(message):
    if message.chat.id not in user_reminders or not user_reminders[message.chat.id]:
        bot.send_message(message.chat.id, "Нет напоминаний")
        return

    text = "Ваши напоминания:\n\n"
    for i, rem in enumerate(user_reminders[message.chat.id], 1):
        text += f"{i}. {rem['day']} {rem['time']} - {rem['text']}\n"

    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == '❌ Удалить')
def delete_reminder(message):
    if message.chat.id not in user_reminders or not user_reminders[message.chat.id]:
        bot.send_message(message.chat.id, "Нет напоминаний для удаления")
        return

    text = "Введите номер напоминания для удаления:"
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, process_delete)


def process_delete(message):
    try:
        num = int(message.text) - 1
        if 0 <= num < len(user_reminders[message.chat.id]):
            user_reminders[message.chat.id].pop(num)
            bot.send_message(message.chat.id, "✅ Удалено!")
        else:
            bot.send_message(message.chat.id, "Неверный номер!")
    except:
        bot.send_message(message.chat.id, "Ошибка!")


# Простой планировщик (для демонстрации)
def check_reminders():
    while True:
        now = datetime.now()
        current_day = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье'][now.weekday()]
        current_time = now.strftime('%H:%M')

        for user_id, reminders in user_reminders.items():
            for rem in reminders:
                if rem['day'] == current_day and rem['time'] == current_time:
                    bot.send_message(user_id, f"🔔 Напоминание: {rem['text']}")

        time.sleep(60)  # Проверяем каждую минуту


# Запуск проверки в отдельном потоке
scheduler_thread = threading.Thread(target=check_reminders)
scheduler_thread.daemon = True
scheduler_thread.start()


@bot.callback_query_handler(func=lambda call: True)
def callback(callback):
    global waiting_for_input
    if callback.data == 'profile':
        help_text = f"""
        🗿Ваш профиль:
        ┏Вес: {FitnessCoefficient.weight}
        ┠Рост: {FitnessCoefficient.height}
        ┠Возраст: {FitnessCoefficient.age}
        ┗Уровень: {FitnessCoefficient.fitness_level}
                    """
        bot.send_message(callback.message.chat.id, text=help_text)

    if callback.data == 'edit_profile':
        markup = types.ReplyKeyboardMarkup()
        button_weight = types.InlineKeyboardButton(text='Ввести вес⚖️', callback_data='weight')
        markup.add(button_weight)
        button_height = types.InlineKeyboardButton(text='Ввести рост🦒', callback_data='height')
        markup.add(button_height)
        button_age = types.InlineKeyboardButton(text='Ввести возраст🎂', callback_data='age')
        markup.add(button_age)
        button_fitness_level = types.InlineKeyboardButton(text='Выбрать уровень подготовки📊', callback_data='fitness_level')
        markup.add(button_fitness_level)
        bot.send_message(callback.message.chat.id, text='Профиль', reply_markup=markup, parse_mode='html')

    if callback.data == 'workout':
        markup = types.InlineKeyboardMarkup()
        button_strength = types.InlineKeyboardButton(text='Силовая (Базовая)🦍', callback_data='strength')
        markup.add(button_strength)
        button_functional = types.InlineKeyboardButton(text='Функциональная (Взрывная сила)🐂', callback_data='functional')
        markup.add(button_functional)
        button_wellness = types.InlineKeyboardButton(text='Оздоровительная (Для осанки)🦙', callback_data='wellness')
        markup.add(button_wellness)
        button_endurance = types.InlineKeyboardButton(text='На Выносливость (Круговая)🐫', callback_data='endurance')
        markup.add(button_endurance)
        button_for_press = types.InlineKeyboardButton(text='Для Пресса и Координации🦈', callback_data='for_press')
        markup.add(button_for_press)
        button_lower_strength = types.InlineKeyboardButton(text='Нижняя Сила (Ноги и кор)🦩', callback_data='lower_strength')
        markup.add(button_lower_strength)
        button_combination = types.InlineKeyboardButton(text='Связка "Турник + Брусья"🐒', callback_data='combination')
        markup.add(button_combination)
        button_full_body = types.InlineKeyboardButton(text='Фулл-Бади (На все тело)🐊', callback_data='full_body')
        markup.add(button_full_body)
        button_street_workout = types.InlineKeyboardButton(text='Уличный Воркаут (Статика и динамика)🐆', callback_data='street_workout')
        markup.add(button_street_workout)
        button_calorie_burning = types.InlineKeyboardButton(text='ВИИТ (Сжигание калорий)🐅', callback_data='calorie_burning')
        markup.add(button_calorie_burning)
        bot.send_message(callback.message.chat.id, text='Готовые тренировки', reply_markup=markup, parse_mode='html')
    if callback.data == 'strength':
        strength_text = f"""
        Тренировка: Силовая (Базовая)🦍
Цель: Развитие максимальной силы.🏆
Отдых: 90-120 секунд.⏱️
1.➣Подтягивания: 4 подхода по {ExerciseCalculator.calculate_pullups()}раз
2.➣Отжимания на брусьях:  4 подхода по {ExerciseCalculator.calculate_dips()}раз
3.➣Приседания:  4 подхода по {ExerciseCalculator.calculate_squats()}раз
4.➣Планка (сек):  3 подхода по {ExerciseCalculator.calculate_plank()}сек
            """
        bot.send_message(callback.message.chat.id, text=strength_text)
    if callback.data == 'functional':
        functional_text = f"""
        Тренировка: Функциональная (Взрывная сила)🐂
Цель: Развитие мощности.🏆
Отдых: 60-75 секунд.⏱️
1.➣Подтягивания с усилием: 4 подхода по {ExerciseCalculator.calculate_pullups()}раз
2.➣Отжимания на брусьях взрывные: 3 подхода по {ExerciseCalculator.calculate_dips()}раз
3.➣Берпи: 3 подхода по {ExerciseCalculator.calculate_burpees()}раз
4.➣Прыжки из приседа: 3 подхода по {ExerciseCalculator.calculate_jump_squats()}раз
            """
        bot.send_message(callback.message.chat.id, text=functional_text)
    if callback.data == 'wellness':
        wellness_text = f"""
        Тренировка: Оздоровительная (Для осанки)🦙
Цель: Укрепление спины и кора.🏆
Отдых: 30-45 секунд.⏱️
1.➣Вис на турнике(сек): 3 подхода по {ExerciseCalculator.calculate_hang_time()}сек
2.➣Подъем ног в висе: 3 подхода по {ExerciseCalculator.calculate_leg_raises()}раз
3.➣Отжимания на брусьях (медленно): 3 подхода по {ExerciseCalculator.calculate_dips()}раз
4.➣Планка(сек): 3 подхода по {ExerciseCalculator.calculate_plank()}сек
            """
        bot.send_message(callback.message.chat.id, text=wellness_text)
    if callback.data == 'endurance':
        endurance_text = f"""
         Тренировка: На Выносливость (Круговая)🐫      
Цель: Развитие выносливости.🏆
Инструкция: Все упражнения подряд, отдых 2 мин после круга. 3-5 кругов.⏱️
1.➣Подтягивания (макс. раз)
2.➣Отжимания на брусьях ({ExerciseCalculator.calculate_dips()} раз)
3.➣Приседания ({ExerciseCalculator.calculate_squats()} раз)
4.➣Берпи ({ExerciseCalculator.calculate_burpees()} раз)
            """
        bot.send_message(callback.message.chat.id, text=endurance_text)
    if callback.data == 'for_press':
        for_press_text = f"""
        Тренировка: Для Пресса и Координации🦈
Цель: Проработка кора.🏆
Отдых: 45-60 секунд.⏱️
1.➣Подъем ног в висе: 4 подхода по {ExerciseCalculator.calculate_leg_raises()}раз
2.➣Уголок на брусьях: 3 подхода по {ExerciseCalculator.calculate_l_sit()}раз
3.➣Скручивания: 3 подхода по {ExerciseCalculator.calculate_crunches()}раз
4.➣Велосипед: 3 подхода по {ExerciseCalculator.calculate_bicycle()}раз
            """
        bot.send_message(callback.message.chat.id, text=for_press_text)
    if callback.data == 'lower_strength':
        lower_strength_text = f"""
        Тренировка: Нижняя Сила (Ноги и кор)🦩
Цель: Развитие низа тела.🏆
Отдых: 60 секунд.⏱️
1.➣Приседания на одной ноге (с опорой): 4 подхода по {ExerciseCalculator.calculate_pistol_squats()}раз
2.➣Выпрыгивания: 3 подхода по {ExerciseCalculator.calculate_jump_squats()}раз
3.➣Подъем ног в висе: 3 подхода по {ExerciseCalculator.calculate_leg_raises()}раз
4.➣Выпады: 3 подхода по {ExerciseCalculator.calculate_lunges()}раз
            """
        bot.send_message(callback.message.chat.id, text=lower_strength_text)
    if callback.data == 'combination':
        combination_text = f"""
        Тренировка: Связка "Турник + Брусья"🐒
Цель: Интенсивная проработка верха тела.🏆
Инструкция: Упражнения парами (суперсеты). Отдых 90 сек после пары.⏱️
Суперсет 1 (4 подхода):
    1.➣Подтягивания ({ExerciseCalculator.calculate_pullups()})
    2.➣Отжимания на брусьях ({ExerciseCalculator.calculate_dips()})
Суперсет 2 (3 подхода):
    1.➣Подъем ног в висе ({ExerciseCalculator.calculate_leg_raises()})
    2.➣Отжимания от пола ({ExerciseCalculator.calculate_pushups()})
            """
        bot.send_message(callback.message.chat.id, text=combination_text)
    if callback.data == 'full_body':
        full_body_text = f"""
        Тренировка: Фулл-Бади (На все тело)🐊
Цель: Равномерная проработка.🏆
Отдых: 60-75 секунд.⏱️
1.➣Подтягивания: 3 подхода по {ExerciseCalculator.calculate_pullups()}раз
2.➣Отжимания на брусьях: 3 подхода по {ExerciseCalculator.calculate_dips()}раз
3.➣Приседания: 3 подхода по {ExerciseCalculator.calculate_squats()}раз
4.➣Подъем ног в висе: 3 подхода по {ExerciseCalculator.calculate_leg_raises()}раз
            """
        bot.send_message(callback.message.chat.id, text=full_body_text)
    if callback.data == 'street_workout':
        street_workout_text = f"""
        Тренировка: Уличный Воркаут (Статика и динамика)🐆
Цель: Развитие силовой выносливости.🏆
Отдых: 90 секунд.⏱️
1.➣Подтягивания: 3 подхода по {ExerciseCalculator.calculate_pullups()}раз
2.➣Передний вис на брусьях: 3 подхода по {ExerciseCalculator.calculate_front_support()}раз
3.➣Отжимания на брусьях: 3 подхода по {ExerciseCalculator.calculate_dips()}раз
4.➣Уголок на брусьях: 3 подхода по {ExerciseCalculator.calculate_l_sit()}раз
            """
        bot.send_message(callback.message.chat.id, text=street_workout_text)
    if callback.data == 'street_workout':
        street_workout_text = f"""
        Тренировка: ВИИТ (Сжигание калорий)🐅
Цель: Максимальная интенсивность.🏆
Инструкция: 40 сек работа / 20 сек отдых. 3-5 кругов.⏱️
1.➣Берпи
2.➣Подтягивания (или вис с подъемом колен)
3.➣Отжимания на брусьях
4.➣Приседания с выпрыгиванием
            """
        bot.send_message(callback.message.chat.id, text=street_workout_text)

    if callback.data == 'notes':
        help_text = """
        Используй команды:
        /add - добавить упражнение
        /list - посмотреть упражнения
        /delete - удалить упражнение
        /clear - очистить все
            """
        bot.send_message(callback.message.chat.id, text=help_text)
    if callback.data == 'reminder':
         set_text = """
         Используй команду:
         /set - установить напоминание
                    """
         bot.send_message(callback.message.chat.id, text=set_text)

    if callback.data == 'exercises':
        markup = types.ReplyKeyboardMarkup()
        button_push_ups = types.InlineKeyboardButton(text='📖Отжимания', callback_data='push-ups')
        markup.add(button_push_ups)
        button_squats = types.InlineKeyboardButton(text='📖Приседания', callback_data='squats')
        markup.add(button_squats)
        button_pull_ups = types.InlineKeyboardButton(text='📖Подтягивания', callback_data='pull_ups')
        markup.add(button_pull_ups)
        button_bars = types.InlineKeyboardButton(text='📖Отжимания на брусьях', callback_data='bars')
        markup.add(button_bars)
        button_twisting = types.InlineKeyboardButton(text='📖Скручивания', callback_data='bars')
        markup.add(button_twisting)
        bot.send_message(callback.message.chat.id, text='Сборник упражнений', reply_markup=markup, parse_mode='html')

    bot.answer_callback_query(callback.id, text="")

#Первая тренировка
@bot.message_handler(func=lambda message: waiting_for_input == 'weight')
def number_handler(message):
    global waiting_for_input
    try:
        FitnessCoefficient.weight = (int(message.text))
        waiting_for_input = ""
        bot.send_message(message.chat.id, f"✅ Вес {FitnessCoefficient.weight} кг сохранён!")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите корректное число!")


@bot.message_handler(func=lambda message: waiting_for_input == 'height')
def number_handler(message):
    global waiting_for_input
    try:
        FitnessCoefficient.height= (int(message.text))
        waiting_for_input = ""
        bot.send_message(message.chat.id, f"✅ Рост {FitnessCoefficient.height} см сохранён!")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите корректное число!")


@bot.message_handler(func=lambda message: waiting_for_input == 'age')
def number_handler(message):
    global waiting_for_input
    try:
        FitnessCoefficient.age = (int(message.text))
        waiting_for_input = ""
        bot.send_message(message.chat.id, f"✅ Возраст {FitnessCoefficient.age} лет сохранён!")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите корректное число!")

@bot.message_handler(content_types=['text'])
def processing(message):
    global waiting_for_input
    if message.text == '📖Отжимания':
        video = open(r"D:\Рабочий стол\Упражнения\istockphoto-1307740744-640_adpp_is.mp4", 'rb')
        bot.send_video(message.from_user.id, video, parse_mode='html')
    if message.text == '📖Приседания':
        video = open(r"D:\Рабочий стол\Упражнения\istockphoto-819399998-640_adpp_is.mp4", 'rb')
        bot.send_video(message.from_user.id, video, parse_mode='html')
    if message.text == '📖Подтягивания':
        video = open(r"D:\Рабочий стол\Упражнения\istockphoto-1354428390-640_adpp_is.mp4", 'rb')
        bot.send_video(message.from_user.id, video, parse_mode='html')
    if message.text == '📖Отжимания на брусьях':
        video = open(r"D:\Рабочий стол\Упражнения\istockphoto-1175028606-640_adpp_is.mp4", 'rb')
        bot.send_video(message.from_user.id, video, parse_mode='html')
    if message.text == '📖Скручивания':
        video = open(r"D:\Рабочий стол\Упражнения\istockphoto-1458561831-640_adpp_is.mp4", 'rb')
        bot.send_video(message.from_user.id, video, parse_mode='html')

    if message.text == 'Ввести вес⚖️':
        waiting_for_input = 'weight'
        bot.send_message(message.chat.id, text="Введите свой вес(кг):")
    if message.text == 'Ввести рост🦒':
        waiting_for_input = 'height'
        bot.send_message(message.chat.id, text="Введите свой рост(см):")
    if message.text == 'Ввести возраст🎂':
        waiting_for_input = 'age'
        bot.send_message(message.chat.id, text="Введите свой возраст:")
    if message.text == 'Выбрать уровень подготовки📊':
        markup = types.ReplyKeyboardMarkup()
        button_beginner = types.InlineKeyboardButton(text='Начинающий🥉', callback_data='beginner')
        markup.add(button_beginner)
        button_intermediate = types.InlineKeyboardButton(text='Продвинутый🥈', callback_data='intermediate')
        markup.add(button_intermediate)
        button_advanced = types.InlineKeyboardButton(text='Профессионал🥇', callback_data='advanced')
        markup.add(button_advanced)
        bot.send_message(message.chat.id, text='Уровень подготовки', reply_markup=markup, parse_mode='html')
    if message.text == 'Начинающий🥉':
        FitnessCoefficient.fitness_level = "beginner"
        bot.send_message(message.chat.id, text="✅ Начинающий🥉 уровень подготовки сохранён!")
    if message.text == 'Продвинутый🥈':
        FitnessCoefficient.fitness_level = "intermediate"
        bot.send_message(message.chat.id, text="✅ Продвинутый🥈 уровень подготовки сохранён!")
    if message.text == 'Профессионал🥇':
        FitnessCoefficient.fitness_level = "advanced"
        bot.send_message(message.chat.id, text="✅ Профессиональный🥇 уровень подготовки сохранён!")

bot.polling(none_stop=True)
