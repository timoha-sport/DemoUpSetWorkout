import json
import os

import threading
import time
from datetime import datetime

import telebot
from telebot import types

from HeartRate import HeartRateCalculator
from Profile import FitnessCoefficient
from Workouts import ExerciseCalculator
from Calories import Calories

bot = telebot.TeleBot("8438729431:AAEZdOQT7de43BWCmDYCVNoeckb4oiIWHTI")
user_name = ""
default = "(по умолчанию)"

@bot.message_handler(commands=['start'])
def start(message):
    global user_name
    user_name = message.from_user.first_name
    welcome = f"""{user_name}, Привет!
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
    button_calories = types.InlineKeyboardButton(text='Добавить калории🍰', callback_data='calories')
    markup.add(button_calories)
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
    global user_name
    if callback.data == 'profile':
        help_text = f"""
        🗿Ваш профиль:
        ┏Имя: {user_name}
        ┠Вес: {FitnessCoefficient.weight}{default}
        ┠Рост: {FitnessCoefficient.height}{default}
        ┠Возраст: {FitnessCoefficient.age}{default}
        ┠Уровень: {FitnessCoefficient.fitness_level}
        ┗Дневная норма: {Calories.daily_calories}/{Calories.calculate_daily_norm(FitnessCoefficient.weight, 
                FitnessCoefficient.height, FitnessCoefficient.age, FitnessCoefficient.fitness_level)} ккал
                    """
        bot.send_message(callback.message.chat.id, text=help_text)

    if callback.data == 'edit_profile':
        markup = types.ReplyKeyboardMarkup()
        button_config = types.InlineKeyboardButton(text='Ввести параметры⚙️', callback_data='config')
        markup.add(button_config)
        bot.send_message(callback.message.chat.id, text='Ввести параметры⚙️', reply_markup=markup, parse_mode='html')

    if callback.data == 'workout':
        markup = types.InlineKeyboardMarkup()
        button_strength = types.InlineKeyboardButton(text='Силовая (Базовая)🦍', callback_data='strength')
        markup.add(button_strength)
        button_functional = types.InlineKeyboardButton(text='Функциональная (Взрывная сила)🐂',
                                                       callback_data='functional')
        markup.add(button_functional)
        button_wellness = types.InlineKeyboardButton(text='Оздоровительная (Для осанки)🦙', callback_data='wellness')
        markup.add(button_wellness)
        button_endurance = types.InlineKeyboardButton(text='На Выносливость (Круговая)🐫', callback_data='endurance')
        markup.add(button_endurance)
        button_for_press = types.InlineKeyboardButton(text='Для Пресса и Координации🦈', callback_data='for_press')
        markup.add(button_for_press)
        button_lower_strength = types.InlineKeyboardButton(text='Нижняя Сила (Ноги и кор)🦩',
                                                           callback_data='lower_strength')
        markup.add(button_lower_strength)
        button_combination = types.InlineKeyboardButton(text='Связка "Турник + Брусья"🐒', callback_data='combination')
        markup.add(button_combination)
        button_full_body = types.InlineKeyboardButton(text='Фулл-Бади (На все тело)🐊', callback_data='full_body')
        markup.add(button_full_body)
        button_street_workout = types.InlineKeyboardButton(text='Уличный Воркаут (Статика и динамика)🐆',
                                                           callback_data='street_workout')
        markup.add(button_street_workout)
        button_calorie_burning = types.InlineKeyboardButton(text='ВИИТ (Сжигание калорий)🐅',
                                                            callback_data='calorie_burning')
        markup.add(button_calorie_burning)
        bot.send_message(callback.message.chat.id, text='Готовые тренировки✅', reply_markup=markup, parse_mode='html')
    if callback.data == 'strength':
        strength_text = f"""
        Тренировка: Силовая (Базовая)🦍
Цель: Развитие максимальной силы.🏆
Отдых: 90-120 секунд.⏱️
Рекомендуемый пульс: {HeartRateCalculator.get_all_workouts_hr(FitnessCoefficient.age)["Strength"]}уд/мин❤️
Калории: {Calories.add_workout_calories(ExerciseCalculator.get_workout("Strength"), FitnessCoefficient.weight)}ккал.🍰
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
Рекомендуемый пульс: {HeartRateCalculator.get_all_workouts_hr(FitnessCoefficient.age)["Power"]}уд/мин❤️
Калории: {Calories.add_workout_calories(ExerciseCalculator.get_workout("Power"), FitnessCoefficient.weight)}ккал.🍰
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
Рекомендуемый пульс: {HeartRateCalculator.get_all_workouts_hr(FitnessCoefficient.age)["Posture"]}уд/мин❤️
Калории: {Calories.add_workout_calories(ExerciseCalculator.get_workout("Posture"), FitnessCoefficient.weight)}ккал.🍰
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
Рекомендуемый пульс: {HeartRateCalculator.get_all_workouts_hr(FitnessCoefficient.age)["Endurance"]}уд/мин❤️
Калории: {Calories.add_workout_calories(ExerciseCalculator.get_workout("Endurance"), FitnessCoefficient.weight)}ккал.🍰
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
Рекомендуемый пульс: {HeartRateCalculator.get_all_workouts_hr(FitnessCoefficient.age)["Core"]}уд/мин❤️
Калории: {Calories.add_workout_calories(ExerciseCalculator.get_workout("Core"), FitnessCoefficient.weight)}ккал.🍰
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
Рекомендуемый пульс: {HeartRateCalculator.get_all_workouts_hr(FitnessCoefficient.age)["Lower"]}уд/мин❤️
Калории: {Calories.add_workout_calories(ExerciseCalculator.get_workout("Lower"), FitnessCoefficient.weight)}ккал.🍰
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
Рекомендуемый пульс: {HeartRateCalculator.get_all_workouts_hr(FitnessCoefficient.age)["Superset"]}уд/мин❤️
Калории: {Calories.add_workout_calories(ExerciseCalculator.get_workout("Superset"), FitnessCoefficient.weight)}ккал.🍰
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
Рекомендуемый пульс: {HeartRateCalculator.get_all_workouts_hr(FitnessCoefficient.age)["Full-Body"]}уд/мин❤️
Калории: {Calories.add_workout_calories(ExerciseCalculator.get_workout("Full-Body"), FitnessCoefficient.weight)}ккал.🍰
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
Рекомендуемый пульс: {HeartRateCalculator.get_all_workouts_hr(FitnessCoefficient.age)["Street"]}уд/мин❤️
Калории: {Calories.add_workout_calories(ExerciseCalculator.get_workout("Street"), FitnessCoefficient.weight)}ккал.🍰
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
Рекомендуемый пульс: {HeartRateCalculator.get_all_workouts_hr(FitnessCoefficient.age)["HIIT"]}уд/мин❤️
Калории: {Calories.add_workout_calories(ExerciseCalculator.get_workout("HIIT"), FitnessCoefficient.weight)}ккал.🍰
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
        markup = types.InlineKeyboardMarkup()
        button_horizontal = types.InlineKeyboardButton(text='На турнике', callback_data='horizontal')
        markup.add(button_horizontal)
        button_bars = types.InlineKeyboardButton(text='На брусьях', callback_data='bars')
        markup.add(button_bars)
        button_inventory = types.InlineKeyboardButton(text='Без инвентаря', callback_data='inventory')
        markup.add(button_inventory)
        bot.send_message(callback.message.chat.id, text='Сборник упражнений📕', reply_markup=markup, parse_mode='html')

    if callback.data == 'horizontal':
        markup = types.ReplyKeyboardMarkup()
        # Турник
        button_pull_ups = types.InlineKeyboardButton(text='Подтягивания💪', callback_data='pull_ups')
        markup.add(button_pull_ups)
        button_hang = types.InlineKeyboardButton(text='Вис на турнике🏋️', callback_data='hang')
        markup.add(button_hang)
        button_leg_raises = types.InlineKeyboardButton(text='Подъем ног в висе🦵', callback_data='leg_raises')
        markup.add(button_leg_raises)
        bot.send_message(callback.message.chat.id, text='На турнике', reply_markup=markup, parse_mode='html')

    if callback.data == 'bars':
        markup = types.ReplyKeyboardMarkup()
        # Брусья
        button_dips = types.InlineKeyboardButton(text='Отжимания на брусьях📊', callback_data='dips')
        markup.add(button_dips)
        button_l_sit = types.InlineKeyboardButton(text='Уголок на брусьях🪑', callback_data='l_sit')
        markup.add(button_l_sit)
        button_front_lever = types.InlineKeyboardButton(text='Передний вис на брусьях🌟', callback_data='front_lever')
        markup.add(button_front_lever)
        bot.send_message(callback.message.chat.id, text='На брусьях', reply_markup=markup, parse_mode='html')

    if callback.data == 'inventory':
        markup = types.ReplyKeyboardMarkup()
        # Без инвентаря
        button_squats = types.InlineKeyboardButton(text='Приседания🏃', callback_data='squats')
        markup.add(button_squats)
        button_pistol_squats = types.InlineKeyboardButton(text='Приседания на одной ноге🦵', callback_data='pistol_squats')
        markup.add(button_pistol_squats)
        button_lunges = types.InlineKeyboardButton(text='Выпады👣', callback_data='lunges')
        markup.add(button_lunges)
        button_jump_squats = types.InlineKeyboardButton(text='Прыжки из приседа🦘', callback_data='jump_squats')
        markup.add(button_jump_squats)
        button_burpees = types.InlineKeyboardButton(text='Берпи⚡', callback_data='burpees')
        markup.add(button_burpees)
        button_pushups = types.InlineKeyboardButton(text='Отжимания от пола🔄', callback_data='pushups')
        markup.add(button_pushups)
        button_plank = types.InlineKeyboardButton(text='Планка⏱️', callback_data='plank')
        markup.add(button_plank)
        button_crunches = types.InlineKeyboardButton(text='Скручивания🌀', callback_data='crunches')
        markup.add(button_crunches)
        button_bicycle = types.InlineKeyboardButton(text='Велосипед🚴', callback_data='bicycle')
        markup.add(button_bicycle)
        bot.send_message(callback.message.chat.id, text='Без инвентаря', reply_markup=markup, parse_mode='html')

    if callback.data == 'calories':
        markup = types.ReplyKeyboardMarkup()
        button_burn_zero = types.InlineKeyboardButton(text='Обнулить ккал🔄', callback_data='zero_calories')
        markup.add(button_burn_zero)
        button_add_calories = types.InlineKeyboardButton(text='Добавить ккал🍔', callback_data='add_calories')
        markup.add(button_add_calories)
        button_burn_calories = types.InlineKeyboardButton(text='Сжечь ккал🔥', callback_data='burn_calories')
        markup.add(button_burn_calories)
        bot.send_message(callback.message.chat.id, text='Калории🍰', reply_markup=markup, parse_mode='html')

    bot.answer_callback_query(callback.id, text="")

@bot.message_handler(func=lambda m: m.text == 'Добавить ккал🍔')
def number_handler(message):
    text = f"""🍔Введите калорийность продукта на 100г и через пробел массу продукта.
Пример: 150 52"""
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, number_handler_add_calories)

def number_handler_add_calories(message):
    try:
        parts = message.text.split(' ', 1)
        calories_per_100g = int(parts[0])
        weight_in_grams = int(parts[1])
        Calories.daily_calories += Calories.calculate_calories(calories_per_100g, weight_in_grams)
        bot.send_message(message.chat.id, f"""✅ Ваше количество ккал на сегодня: {Calories.daily_calories}ккал!\n
Было добавлено: {Calories.calculate_calories(calories_per_100g, weight_in_grams)} ккал""")
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Ошибка типа данных!\nИспользуйте цифры!")
        bot.register_next_step_handler(msg, number_handler_config)
    except Exception:
        msg = bot.send_message(message.chat.id, "❌ Ошибка формата! \nВведите калорийность продукта(грамм) и массу продукта(грамм) через пробел!")
        bot.register_next_step_handler(msg, number_handler_config)

@bot.message_handler(func=lambda m: m.text == 'Сжечь ккал🔥')
def number_handler(message):
    msg = bot.send_message(message.chat.id, "🔥Введите количество сожженных ккал:")
    bot.register_next_step_handler(msg, number_handler_clear)

def number_handler_clear(message):
    global default
    if 0 > Calories.daily_calories - (int(message.text)):
        bot.send_message(message.chat.id, "❌ Количество калорий больше чем вы можете сжечь!")
    else:
        try:
            Calories.daily_calories -= (int(message.text))
            bot.send_message(message.chat.id, f"✅ Ваше количество ккал на сегодня: {Calories.daily_calories}ккал!")
        except ValueError:
            bot.send_message(message.chat.id, "❌ Введите корректное число!")

@bot.message_handler(func=lambda m: m.text == 'Обнулить ккал🔄')
def number_handler(message):
    Calories.daily_calories = 0
    bot.send_message(message.chat.id, text="🔄Калории обнулены")

@bot.message_handler(func=lambda m: m.text == 'Начинающий🥉')
def number_handler(message):
    FitnessCoefficient.fitness_level = "beginner"
    bot.send_message(message.chat.id, text="✅ Начинающий🥉 уровень подготовки сохранён!\n Можете вернуться в /menu")

@bot.message_handler(func=lambda m: m.text == 'Продвинутый🥈')
def number_handler(message):
    FitnessCoefficient.fitness_level = "intermediate"
    bot.send_message(message.chat.id, text="✅ Продвинутый🥈 уровень подготовки сохранён!\n Можете вернуться в /menu")

@bot.message_handler(func=lambda m: m.text == 'Профессионал🥇')
def number_handler(message):
    FitnessCoefficient.fitness_level = "advanced"
    bot.send_message(message.chat.id, text="✅ Профессионал🥇 уровень подготовки сохранён!\n Можете вернуться в /menu")



@bot.message_handler(func=lambda m: m.text == "Ввести параметры⚙️")
def number_handler(message):
    msg = bot.send_message(message.chat.id, "Введите вес(кг), рост(см) и возраст(лет) в таком формате:'70 180 25'")
    bot.register_next_step_handler(msg, number_handler_config)

def number_handler_config(message):
    global default
    try:
        parts = message.text.split(' ', 2)
        FitnessCoefficient.weight = int(parts[0])
        FitnessCoefficient.height = int(parts[1])
        FitnessCoefficient.age = int(parts[2])
        default = ""
        bot.send_message(message.chat.id, f"""✅ Параметры {FitnessCoefficient.weight}кг, {FitnessCoefficient.height}см, {FitnessCoefficient.age}лет сохранены!""")
        number_handler_fit_level(message)
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Ошибка типа данных!\nИспользуйте цифры!")
        bot.register_next_step_handler(msg, number_handler_config)
    except Exception:
        msg = bot.send_message(message.chat.id, "❌ Ошибка формата! \nВведите вес(кг), рост(см), возраст(лет) через пробел!")
        bot.register_next_step_handler(msg, number_handler_config)

def number_handler_fit_level(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Профессионал🥇')
    markup.add('Начинающий🥉', 'Продвинутый🥈')
    bot.send_message(message.chat.id, "Выбери свой уровень подготовки!💪", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def processing(message):
    # Турник
    if message.text == 'Подтягивания💪':
        video = open(r"D:\Рабочий стол\Упражнения\istockphoto-1354428390-640_adpp_is.mp4", 'rb')
        bot.send_video(message.from_user.id, video, parse_mode='html')
    if message.text == 'Вис на турнике🏋️':
        video = open(r"D:\Рабочий стол\Упражнения\istockphoto-1758996530-640_adpp_is.mp4", 'rb')
        bot.send_video(message.from_user.id, video, parse_mode='html')
    if message.text == 'Подъем ног в висе🦵':
        video = open(r"D:\Рабочий стол\Упражнения\istockphoto-1553010542-640_adpp_is.mp4", 'rb')
        bot.send_video(message.from_user.id, video, parse_mode='html')
    # Брусья
    if message.text == 'Отжимания на брусьях📊':
        video = open(r"D:\Рабочий стол\Упражнения\istockphoto-1175028606-640_adpp_is.mp4", 'rb')
        bot.send_video(message.from_user.id, video, parse_mode='html')
    if message.text == 'Уголок на брусьях🪑':
        photo = open(r"D:\Рабочий стол\Упражнения\4fab467e6f69f505d893579771f680ef.jpg", 'rb')
        bot.send_photo(message.from_user.id, photo, parse_mode='html')
    if message.text == 'Передний вис на брусьях🌟':
        photo = open(r"D:\Рабочий стол\Упражнения\8f310a0667e011b0a59f85b52d6127f4.jpg", 'rb')
        bot.send_photo(message.from_user.id, photo, parse_mode='html')
    # Без инвентаря
    if message.text == 'Приседания🏃':
        video = open(r"D:\Рабочий стол\Упражнения\istockphoto-819399998-640_adpp_is.mp4", 'rb')
        bot.send_video(message.from_user.id, video, parse_mode='html')
    if message.text == 'Приседания на одной ноге🦵':
        video = open(r"D:\Рабочий стол\Упражнения\istockphoto-1286339867-640_adpp_is.mp4", 'rb')
        bot.send_video(message.from_user.id, video, parse_mode='html')
    if message.text == 'Выпады👣':
        video = open(r"D:\Рабочий стол\Упражнения\istockphoto-819176128-640_adpp_is.mp4", 'rb')
        bot.send_video(message.from_user.id, video, parse_mode='html')
    if message.text == 'Прыжки из приседа🦘':
        video = open(r"D:\Рабочий стол\Упражнения\istockphoto-1566551937-640_adpp_is.mp4", 'rb')
        bot.send_video(message.from_user.id, video, parse_mode='html')
    if message.text == 'Берпи⚡':
        video = open(r"D:\Рабочий стол\Упражнения\istockphoto-478074290-640_adpp_is.mp4", 'rb')
        bot.send_video(message.from_user.id, video, parse_mode='html')
    if message.text == 'Отжимания от пола🔄':
        video = open(r"D:\Рабочий стол\Упражнения\istockphoto-1307740744-640_adpp_is.mp4", 'rb')
        bot.send_video(message.from_user.id, video, parse_mode='html')
    if message.text == 'Планка⏱️':
        video = open(r"D:\Рабочий стол\Упражнения\istockphoto-966411966-640_adpp_is.mp4", 'rb')
        bot.send_video(message.from_user.id, video, parse_mode='html')
    if message.text == 'Скручивания🌀':
        video = open(r"D:\Рабочий стол\Упражнения\istockphoto-472821189-640_adpp_is.mp4", 'rb')
        bot.send_video(message.from_user.id, video, parse_mode='html')
    if message.text == 'Велосипед🚴':
        video = open(r"D:\Рабочий стол\Упражнения\istockphoto-1389749311-640_adpp_is.mp4", 'rb')
        bot.send_video(message.from_user.id, video, parse_mode='html')
bot.polling(none_stop=True)
