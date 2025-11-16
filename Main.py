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

@bot.message_handler(commands=['start'])
def start(message):
    global user_name
    user_name = message.from_user.first_name
    welcome = f"""{user_name}, Привет!
  ➣Меня зовут Арнольд🦍, я тебя приобщу к ЗОЖ (здоровому образу жизни).\n
  ➣Вноси свои физические данные в разделе "Изменить профиль⚙️" и выбирай тренировку по душе!\n
  ➣Открой /menu, что бы ознакомиться с функционалом.
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
    button_notes = types.InlineKeyboardButton(text='Заметки📃', callback_data='notes')
    markup.add(button_notes)
    button_reminder = types.InlineKeyboardButton(text='Установить напоминание📆', callback_data='reminder')
    markup.add(button_reminder)
    button_exercises = types.InlineKeyboardButton(text='Сборник упражнений📕', callback_data='exercises')
    markup.add(button_exercises)
    button_calories = types.InlineKeyboardButton(text='Добавить калории🍰', callback_data='calories')
    markup.add(button_calories)
    button_recipes = types.InlineKeyboardButton(text='Рецепты🍽️', callback_data='recipes')
    markup.add(button_recipes)
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


@bot.message_handler(commands=['notes'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('➕Добавить📌', '❌Удалить📌')
    markup.add('🗑️Очистить📌', '📋Список📌')
    bot.send_message(message.chat.id, "Я напомню нужные тебе события!", reply_markup=markup)


# Команда /add - добавить заметку
@bot.message_handler(func=lambda m: m.text == '➕Добавить📌')
def add_note(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "📝 Напиши текст заметки:")
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
    bot.send_message(chat_id, f"✅ Заметка #{note_id} сохранена!")


# Команда /list - показать все заметки
@bot.message_handler(func=lambda m: m.text == '📋Список📌')
def list_notes(message):
    chat_id = message.chat.id
    notes = load_notes()

    user_notes = notes.get(str(chat_id), {})

    if not user_notes:
        bot.send_message(chat_id, "📭 У тебя пока нет заметок")
        return

    response = "📋 Твои заметки:\n\n"
    for note_id, note_text in user_notes.items():
        response += f"#{note_id}: {note_text}\n\n"

    bot.send_message(chat_id, response)


# Команда /delete - удалить заметку
@bot.message_handler(func=lambda m: m.text == '❌Удалить📌')
def delete_note(message):
    chat_id = message.chat.id
    notes = load_notes()

    user_notes = notes.get(str(chat_id), {})

    if not user_notes:
        bot.send_message(chat_id, "📭 Нечего удалять - заметок нет")
        return

    # Показываем список заметок для удаления
    response = "❌ Какое заметку удалить? Напиши номер:\n\n"
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
            bot.send_message(chat_id, f"✅ Заметка #{note_id} удалена")
        else:
            bot.send_message(chat_id, f"⚠️ Заметка #{note_id} не найдена!")

    except ValueError:
        bot.send_message(chat_id, "❌ Напиши номер заметки цифрой")


# Команда /clear - очистить все заметки
@bot.message_handler(func=lambda m: m.text == '🗑️Очистить📌')
def clear_notes(message):
    chat_id = message.chat.id
    notes = load_notes()

    if str(chat_id) in notes and notes[str(chat_id)]:
        notes[str(chat_id)] = {}
        save_notes(notes)
        bot.send_message(chat_id, "🗑️ Все заметки удалены!")
    else:
        bot.send_message(chat_id, "📭 Нечего удалять - заметок нет")


# Простое хранилище в памяти
user_reminders = {}


@bot.message_handler(commands=['reminders'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('➕Добавить⏰', '❌Удалить⏰')
    markup.add('📋Список⏰')
    bot.send_message(message.chat.id, "Я напомню нужные тебе события!", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == '➕Добавить⏰')
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


@bot.message_handler(func=lambda m: m.text == '📋Список⏰')
def list_reminders(message):
    if message.chat.id not in user_reminders or not user_reminders[message.chat.id]:
        bot.send_message(message.chat.id, "Нет напоминаний")
        return

    text = "Ваши напоминания:\n\n"
    for i, rem in enumerate(user_reminders[message.chat.id], 1):
        text += f"{i}. {rem['day']} {rem['time']} - {rem['text']}\n"

    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == '❌Удалить⏰')
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
        user_id = callback.from_user.id
        profile = get_user_profile(user_id)

        weight = profile.get('weight', 'Не указан')
        height = profile.get('height', 'Не указан')
        age = profile.get('age', 'Не указан')
        name = profile.get('name', 'Не указано')
        calories = profile.get('calories', 'Не указано')
        day_calories = profile.get('day_calories', 0)
        # Преобразуем уровень подготовки в читаемый вид
        fitness_level = profile.get('fitness_level', 'Не указан')
        level_display = {
            'beginner': 'Начинающий🥉',
            'intermediate': 'Продвинутый🥈',
            'advanced': 'Профессионал🥇'
        }.get(fitness_level, fitness_level)

        profile_text = f"""
    🗿Ваш профиль:
    ┏Имя: {name}
    ┠Вес: {weight} кг
    ┠Рост: {height} см
    ┠Возраст: {age} лет
    ┠Уровень: {level_display}
    ┗Дневная норма: {day_calories}/{calories} ккал
                """
        bot.send_message(callback.message.chat.id, profile_text)

    if callback.data == 'edit_profile':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
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
Рекомендуемый пульс: {HeartRateCalculator.get_all_workouts_hr(get_user_age(callback.message.chat.id))["Strength"]}уд/мин❤️
Калории: {Calories.add_workout_calories(ExerciseCalculator.get_workout("Strength",get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id)), get_user_weight(callback.message.chat.id))}ккал.🍰
1.➣Подтягивания: 4 подхода по {ExerciseCalculator.calculate_pullups(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
2.➣Отжимания на брусьях:  4 подхода по {ExerciseCalculator.calculate_dips(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
3.➣Приседания:  4 подхода по {ExerciseCalculator.calculate_squats(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
4.➣Планка (сек):  3 подхода по {ExerciseCalculator.calculate_plank(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} сек
            """
        bot.send_message(callback.message.chat.id, text=strength_text)
    if callback.data == 'functional':
        functional_text = f"""
        Тренировка: Функциональная (Взрывная сила)🐂
Цель: Развитие мощности.🏆
Отдых: 60-75 секунд.⏱️
Рекомендуемый пульс: {HeartRateCalculator.get_all_workouts_hr(get_user_age(callback.message.chat.id))["Power"]}уд/мин❤️
Калории: {Calories.add_workout_calories(ExerciseCalculator.get_workout("Power",get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id)), get_user_weight(callback.message.chat.id))}ккал.🍰
1.➣Подтягивания с усилием: 4 подхода по {ExerciseCalculator.calculate_pullups(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
2.➣Отжимания на брусьях взрывные: 3 подхода по {ExerciseCalculator.calculate_dips(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
3.➣Берпи: 3 подхода по {ExerciseCalculator.calculate_burpees(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
4.➣Прыжки из приседа: 3 подхода по {ExerciseCalculator.calculate_jump_squats(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
            """
        bot.send_message(callback.message.chat.id, text=functional_text)
    if callback.data == 'wellness':
        wellness_text = f"""
        Тренировка: Оздоровительная (Для осанки)🦙
Цель: Укрепление спины и кора.🏆
Отдых: 30-45 секунд.⏱️
Рекомендуемый пульс: {HeartRateCalculator.get_all_workouts_hr(get_user_age(callback.message.chat.id))["Posture"]}уд/мин❤️
Калории: {Calories.add_workout_calories(ExerciseCalculator.get_workout("Posture",get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id)), get_user_weight(callback.message.chat.id))}ккал.🍰
1.➣Вис на турнике(сек): 3 подхода по {ExerciseCalculator.calculate_hang_time(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} сек
2.➣Подъем ног в висе: 3 подхода по {ExerciseCalculator.calculate_leg_raises(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
3.➣Отжимания на брусьях (медленно): 3 подхода по {ExerciseCalculator.calculate_dips(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
4.➣Планка(сек): 3 подхода по {ExerciseCalculator.calculate_plank(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} сек
            """
        bot.send_message(callback.message.chat.id, text=wellness_text)
    if callback.data == 'endurance':
        endurance_text = f"""
         Тренировка: На Выносливость (Круговая)🐫      
Цель: Развитие выносливости.🏆
Инструкция: Все упражнения подряд, отдых 2 мин после круга. 3-5 кругов.⏱️
Рекомендуемый пульс: {HeartRateCalculator.get_all_workouts_hr(get_user_age(callback.message.chat.id))["Endurance"]}уд/мин❤️
Калории: {Calories.add_workout_calories(ExerciseCalculator.get_workout("Endurance",get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id)), get_user_weight(callback.message.chat.id))}ккал.🍰
1.➣Подтягивания: макс. раз
2.➣Отжимания на брусьях: {ExerciseCalculator.calculate_dips(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
3.➣Приседания: {ExerciseCalculator.calculate_squats(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
4.➣Берпи: {ExerciseCalculator.calculate_burpees(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
            """
        bot.send_message(callback.message.chat.id, text=endurance_text)
    if callback.data == 'for_press':
        for_press_text = f"""
        Тренировка: Для Пресса и Координации🦈
Цель: Проработка кора.🏆
Отдых: 45-60 секунд.⏱️
Рекомендуемый пульс: {HeartRateCalculator.get_all_workouts_hr(get_user_age(callback.message.chat.id))["Core"]}уд/мин❤️
Калории: {Calories.add_workout_calories(ExerciseCalculator.get_workout("Core",get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id)), get_user_weight(callback.message.chat.id))}ккал.🍰
1.➣Подъем ног в висе: 4 подхода по {ExerciseCalculator.calculate_leg_raises(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
2.➣Уголок на брусьях: 3 подхода по {ExerciseCalculator.calculate_l_sit(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
3.➣Скручивания: 3 подхода по {ExerciseCalculator.calculate_crunches(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
4.➣Велосипед: 3 подхода по {ExerciseCalculator.calculate_bicycle(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
            """
        bot.send_message(callback.message.chat.id, text=for_press_text)
    if callback.data == 'lower_strength':
        lower_strength_text = f"""
        Тренировка: Нижняя Сила (Ноги и кор)🦩
Цель: Развитие низа тела.🏆
Отдых: 60 секунд.⏱️
Рекомендуемый пульс: {HeartRateCalculator.get_all_workouts_hr(get_user_age(callback.message.chat.id))["Lower"]}уд/мин❤️
Калории: {Calories.add_workout_calories(ExerciseCalculator.get_workout("Lower",get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id)), get_user_weight(callback.message.chat.id))}ккал.🍰
1.➣Приседания на одной ноге (с опорой): 4 подхода по {ExerciseCalculator.calculate_pistol_squats(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
2.➣Выпрыгивания: 3 подхода по {ExerciseCalculator.calculate_jump_squats(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
3.➣Подъем ног в висе: 3 подхода по {ExerciseCalculator.calculate_leg_raises(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
4.➣Выпады: 3 подхода по {ExerciseCalculator.calculate_lunges(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
            """
        bot.send_message(callback.message.chat.id, text=lower_strength_text)
    if callback.data == 'combination':
        combination_text = f"""
        Тренировка: Связка "Турник + Брусья"🐒
Цель: Интенсивная проработка верха тела.🏆
Инструкция: Упражнения парами (суперсеты). Отдых 90 сек после пары.⏱️
Рекомендуемый пульс: {HeartRateCalculator.get_all_workouts_hr(get_user_age(callback.message.chat.id))["Superset"]}уд/мин❤️
Калории: {Calories.add_workout_calories(ExerciseCalculator.get_workout("Superset",get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id)), get_user_weight(callback.message.chat.id))}ккал.🍰
Суперсет 1 (4 подхода):
    1.➣Подтягивания: {ExerciseCalculator.calculate_pullups(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
    2.➣Отжимания на брусьях: {ExerciseCalculator.calculate_dips(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
Суперсет 2 (3 подхода):
    1.➣Подъем ног в висе: {ExerciseCalculator.calculate_leg_raises(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
    2.➣Отжимания от пола: {ExerciseCalculator.calculate_pushups(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
            """
        bot.send_message(callback.message.chat.id, text=combination_text)
    if callback.data == 'full_body':
        full_body_text = f"""
        Тренировка: Фулл-Бади (На все тело)🐊
Цель: Равномерная проработка.🏆
Отдых: 60-75 секунд.⏱️
Рекомендуемый пульс: {HeartRateCalculator.get_all_workouts_hr(get_user_age(callback.message.chat.id))["Full-Body"]}уд/мин❤️
Калории: {Calories.add_workout_calories(ExerciseCalculator.get_workout("Full-Body",get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id)), get_user_weight(callback.message.chat.id))}ккал.🍰
1.➣Подтягивания: 3 подхода по {ExerciseCalculator.calculate_pullups(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
2.➣Отжимания на брусьях: 3 подхода по {ExerciseCalculator.calculate_dips(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
3.➣Приседания: 3 подхода по {ExerciseCalculator.calculate_squats(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
4.➣Подъем ног в висе: 3 подхода по {ExerciseCalculator.calculate_leg_raises(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
            """
        bot.send_message(callback.message.chat.id, text=full_body_text)
    if callback.data == 'street_workout':
        street_workout_text = f"""
        Тренировка: Уличный Воркаут (Статика и динамика)🐆
Цель: Развитие силовой выносливости.🏆
Отдых: 90 секунд.⏱️
Рекомендуемый пульс: {HeartRateCalculator.get_all_workouts_hr(get_user_age(callback.message.chat.id))["Street"]}уд/мин❤️
Калории: {Calories.add_workout_calories(ExerciseCalculator.get_workout("Street",get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id)), get_user_weight(callback.message.chat.id))}ккал.🍰
1.➣Подтягивания: 3 подхода по {ExerciseCalculator.calculate_pullups(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
2.➣Передний вис на брусьях: 3 подхода по {ExerciseCalculator.calculate_front_support(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
3.➣Отжимания на брусьях: 3 подхода по {ExerciseCalculator.calculate_dips(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
4.➣Уголок на брусьях: 3 подхода по {ExerciseCalculator.calculate_l_sit(get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id))} раз
            """
        bot.send_message(callback.message.chat.id, text=street_workout_text)
    if callback.data == 'street_workout':
        street_workout_text = f"""
        Тренировка: ВИИТ (Сжигание калорий)🐅
Цель: Максимальная интенсивность.🏆
Инструкция: 40 сек работа / 20 сек отдых. 3-5 кругов.⏱️
Рекомендуемый пульс: {HeartRateCalculator.get_all_workouts_hr(get_user_age(callback.message.chat.id))["HIIT"]}уд/мин❤️
Калории: {Calories.add_workout_calories(ExerciseCalculator.get_workout("HIIT",get_user_weight(callback.message.chat.id), get_user_height(callback.message.chat.id), get_user_age(callback.message.chat.id), get_user_fitness_level(callback.message.chat.id)), get_user_weight(callback.message.chat.id))}ккал.🍰
1.➣Берпи
2.➣Подтягивания (или вис с подъемом колен)
3.➣Отжимания на брусьях
4.➣Приседания с выпрыгиванием
            """
        bot.send_message(callback.message.chat.id, text=street_workout_text)

    if callback.data == 'notes':
        help_text = """
        Используй команду:
        /notes - заметки 
            """
        bot.send_message(callback.message.chat.id, text=help_text)
    if callback.data == 'reminder':
        set_text = """
         Используй команду:
         /reminders - напоминания
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
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # Турник
        button_pull_ups = types.InlineKeyboardButton(text='Подтягивания💪', callback_data='pull_ups')
        markup.add(button_pull_ups)
        button_hang = types.InlineKeyboardButton(text='Вис на турнике🏋️', callback_data='hang')
        markup.add(button_hang)
        button_leg_raises = types.InlineKeyboardButton(text='Подъем ног в висе🦵', callback_data='leg_raises')
        markup.add(button_leg_raises)
        bot.send_message(callback.message.chat.id, text='На турнике', reply_markup=markup, parse_mode='html')

    if callback.data == 'bars':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # Брусья
        button_dips = types.InlineKeyboardButton(text='Отжимания на брусьях📊', callback_data='dips')
        markup.add(button_dips)
        button_l_sit = types.InlineKeyboardButton(text='Уголок на брусьях🪑', callback_data='l_sit')
        markup.add(button_l_sit)
        button_front_lever = types.InlineKeyboardButton(text='Передний вис на брусьях🌟', callback_data='front_lever')
        markup.add(button_front_lever)
        bot.send_message(callback.message.chat.id, text='На брусьях', reply_markup=markup, parse_mode='html')

    if callback.data == 'inventory':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
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
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_burn_zero = types.InlineKeyboardButton(text='Обнулить ккал🔄', callback_data='zero_calories')
        button_add_calories = types.InlineKeyboardButton(text='Добавить ккал🍔', callback_data='add_calories')
        button_burn_calories = types.InlineKeyboardButton(text='Сжечь ккал🔥', callback_data='burn_calories')
        markup.add(button_add_calories, button_burn_calories)
        markup.add(button_burn_zero)
        bot.send_message(callback.message.chat.id, text='Калории🍰', reply_markup=markup, parse_mode='html')

    if callback.data == 'recipes':
        text = '🍽️Рецепты, от которых ты не поправишься:\n http://propernutritionarnold.tilda.ws/'
        bot.send_message(callback.message.chat.id, text, disable_web_page_preview=True)
    bot.answer_callback_query(callback.id, text="")


USER_FILE = "user_data.json"


def load_user_data():
    """Загружает данные всех пользователей из JSON"""
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Конвертируем ключи пользователей в int
            return {int(k): v for k, v in data.items()}
    return {}


def save_user_data(user_data):
    """Сохраняет данные всех пользователей в JSON"""
    with open(USER_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)


def get_user_profile(user_id):
    """Получает профиль конкретного пользователя"""
    user_data = load_user_data()
    return user_data.get(user_id, {})


def get_user_weight(user_id):
    """Получает вес пользователя"""
    profile = get_user_profile(user_id)
    return profile.get('weight')


def get_user_height(user_id):
    """Получает рост пользователя"""
    profile = get_user_profile(user_id)
    return profile.get('height')


def get_user_age(user_id):
    """Получает возраст пользователя"""
    profile = get_user_profile(user_id)
    return profile.get('age')


def get_user_fitness_level(user_id):
    """Получает уровень подготовки пользователя"""
    profile = get_user_profile(user_id)
    return profile.get('fitness_level', 'beginner')

def get_day_calories(user_id):
    profile = get_user_profile(user_id)
    return profile.get('day_calories')

def update_user_calories(user_id, calories):
    """Сеттер для обновления веса пользователя"""
    user_data = load_user_data()

    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]['day_calories'] = user_data[user_id]['day_calories'] + calories
    save_user_data(user_data)


def burn_user_calories(user_id, calories):
    user_data = load_user_data()

    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]['day_calories'] = user_data[user_id]['day_calories'] - calories
    save_user_data(user_data)

def zero_user_calories(user_id):
    user_data = load_user_data()

    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]['day_calories'] = 0
    save_user_data(user_data)

@bot.message_handler(func=lambda m: m.text == 'Ввести параметры⚙️')
def number_handler(message):
    msg = bot.send_message(message.chat.id, "Введите вес(кг), рост(см) и возраст(лет) в таком формате:'70 180 25'")
    bot.register_next_step_handler(msg, process_user_data)


def process_user_data(message):
    chat_id = message.chat.id

    try:
        parts = message.text.split(' ', 2)
        weight = int(parts[0])
        height = int(parts[1])
        age = int(parts[2])

        # Загружаем текущие данные
        user_data = load_user_data()

        # Создаем или обновляем запись пользователя
        user_data[chat_id] = {
            'weight': weight,
            'height': height,
            'age': age,
            'name': message.from_user.first_name,
            'fitness_level': 'beginner',
            'calories' : Calories.calculate_daily_norm(weight, height, age, get_user_fitness_level(chat_id)),
            'day_calories' : 0
        }

        # Сохраняем обратно в JSON
        save_user_data(user_data)

        bot.send_message(chat_id, f"✅ Данные сохранены!\nВес: {weight}кг\nРост: {height}см\nВозраст: {age}лет")
        number_handler_fit_level(message)  # переходим к выбору уровня

    except ValueError:
        bot.send_message(chat_id, "❌ Ошибка! Используйте цифры в формате: '70 180 25'")
    except Exception as e:
        bot.send_message(chat_id, "❌ Ошибка формата! Введите: вес рост возраст")


def number_handler_fit_level(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Профессионал🥇')
    markup.add('Начинающий🥉', 'Продвинутый🥈')
    bot.send_message(message.chat.id, "Выбери свой уровень подготовки!💪", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == 'Начинающий🥉')
def number_handler(message):
    user_id = message.chat.id
    FitnessCoefficient.fitness_level = "beginner"

    # Сохраняем уровень подготовки в JSON
    user_data = load_user_data()
    if user_id in user_data:
        user_data[user_id]['fitness_level'] = "beginner"
        save_user_data(user_data)

    bot.send_message(message.chat.id, text="✅ Начинающий🥉 уровень подготовки сохранён!\n Можете вернуться в /menu")


@bot.message_handler(func=lambda m: m.text == 'Продвинутый🥈')
def number_handler(message):
    user_id = message.chat.id
    FitnessCoefficient.fitness_level = "intermediate"

    # Сохраняем уровень подготовки в JSON
    user_data = load_user_data()
    if user_id in user_data:
        user_data[user_id]['fitness_level'] = "intermediate"
        save_user_data(user_data)

    bot.send_message(message.chat.id, text="✅ Продвинутый🥈 уровень подготовки сохранён!\n Можете вернуться в /menu")


@bot.message_handler(func=lambda m: m.text == 'Профессионал🥇')
def number_handler(message):
    user_id = message.chat.id
    FitnessCoefficient.fitness_level = "advanced"

    # Сохраняем уровень подготовки в JSON
    user_data = load_user_data()
    if user_id in user_data:
        user_data[user_id]['fitness_level'] = "advanced"
        save_user_data(user_data)

    bot.send_message(message.chat.id, text="✅ Профессионал🥇 уровень подготовки сохранён!\n Можете вернуться в /menu")


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
        update_user_calories(message.chat.id, Calories.calculate_calories(calories_per_100g, weight_in_grams))
        bot.send_message(message.chat.id, f"""✅ Ваше количество ккал на сегодня: {get_day_calories(message.chat.id)}ккал!\n
Было добавлено: {round((weight_in_grams / 100) * calories_per_100g)} ккал""")
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Ошибка типа данных!\nИспользуйте цифры!")
        bot.register_next_step_handler(msg, number_handler_add_calories)
    except Exception as e:
        msg = bot.send_message(message.chat.id, "❌ Ошибка формата! \nВведите калорийность продукта(грамм) и массу продукта(грамм) через пробел!")
        bot.register_next_step_handler(msg, number_handler_add_calories)

@bot.message_handler(func=lambda m: m.text == 'Сжечь ккал🔥')
def number_handler(message):
    msg = bot.send_message(message.chat.id, "🔥Введите количество сожженных ккал:")
    bot.register_next_step_handler(msg, number_handler_clear)

def number_handler_clear(message):
    global default
    try:
        if 0 > get_day_calories(message.chat.id) - (int(message.text)):
            msg = bot.send_message(message.chat.id, "❌ Количество калорий больше чем вы можете сжечь!")
            bot.register_next_step_handler(msg, number_handler_clear)
        else:
            burn_user_calories(message.chat.id, int(message.text))
            bot.send_message(message.chat.id, f"✅ Ваше количество ккал на сегодня: {round(get_day_calories(message.chat.id))}ккал!")
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Введите корректное число!")
        bot.register_next_step_handler(msg, number_handler_clear)

@bot.message_handler(func=lambda m: m.text == 'Обнулить ккал🔄')
def number_handler(message):
    zero_user_calories(message.chat.id)
    bot.send_message(message.chat.id, text="🔄Калории обнулены")

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
