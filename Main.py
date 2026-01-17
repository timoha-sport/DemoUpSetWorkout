import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

import json
import os
import random
from typing import Dict, Any, Optional

from HeartRate import HeartRateCalculator
from Profile import FitnessCoefficient
from Workouts import ExerciseCalculator
from Calories import Calories

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token="8438729431:AAEZdOQT7de43BWCmDYCVNoeckb4oiIWHTI")
dp = Dispatcher(storage=MemoryStorage())

# Константы
NOTES_FILE = "notes.json"
USER_FILE = "user_data.json"
REMINDERS_FILE = "reminders.json"

# Хранилище напоминаний в памяти (временное)
user_reminders: Dict[int, list] = {}


# ====================== КЛАССЫ СОСТОЯНИЙ ======================

class UserProfile(StatesGroup):
    """Состояния для создания/редактирования профиля"""
    waiting_for_params = State()
    waiting_for_fitness_level = State()


class NoteStates(StatesGroup):
    """Состояния для работы с заметками"""
    waiting_for_note_text = State()
    waiting_for_note_delete = State()


class CalorieStates(StatesGroup):
    """Состояния для работы с калориями"""
    waiting_for_calories_add = State()
    waiting_for_calories_burn = State()


class ReminderStates(StatesGroup):
    """Состояния для работы с напоминаниями"""
    waiting_for_reminder = State()
    waiting_for_reminder_delete = State()


# ====================== УТИЛИТЫ ДЛЯ РАБОТЫ С ДАННЫМИ ======================

def load_json_file(filename: str, default_factory=dict) -> dict:
    """Загружает JSON файл, возвращает dict"""
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Конвертируем строковые ключи в int для user_id
                if filename == USER_FILE:
                    return {int(k): v for k, v in data.items()}
                elif filename == NOTES_FILE:
                    # Для заметок конвертируем вложенные ключи тоже
                    result = {}
                    for user_id_str, notes in data.items():
                        result[int(user_id_str)] = {
                            int(k): v for k, v in notes.items()
                        }
                    return result
                return data
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
    return default_factory()


def save_json_file(filename: str, data: dict):
    """Сохраняет данные в JSON файл"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving {filename}: {e}")


def get_user_profile(user_id: int) -> dict:
    """Возвращает профиль пользователя"""
    user_data = load_json_file(USER_FILE)
    return user_data.get(user_id, {})


def save_user_profile(user_id: int, profile_data: dict):
    """Сохраняет профиль пользователя"""
    user_data = load_json_file(USER_FILE)
    user_data[user_id] = profile_data
    save_json_file(USER_FILE, user_data)


def update_user_field(user_id: int, field: str, value: Any):
    """Обновляет конкретное поле профиля пользователя"""
    user_data = load_json_file(USER_FILE)
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id][field] = value
    save_json_file(USER_FILE, user_data)


def get_user_field(user_id: int, field: str, default=None):
    """Возвращает значение поля из профиля пользователя"""
    profile = get_user_profile(user_id)
    return profile.get(field, default)


def check_profile_exists(user_id: int) -> bool:
    """Проверяет, существует ли полный профиль пользователя"""
    profile = get_user_profile(user_id)
    required_fields = ['weight', 'height', 'age', 'name']
    return all(field in profile for field in required_fields)


def renumber_notes(user_notes: dict) -> dict:
    """Перенумеровывает заметки пользователя"""
    if not user_notes:
        return {}

    sorted_notes = sorted(user_notes.items())
    return {i + 1: note_text for i, (old_id, note_text) in enumerate(sorted_notes)}


# ====================== КЛАВИАТУРЫ ======================

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура главного меню"""
    builder = InlineKeyboardBuilder()

    buttons = [
        ("Профиль🪪", "profile"),
        ("Изменить профиль⚙️", "edit_profile"),
        ("Истории Арнольда🦍", "plot"),
        ("Тренировки💪", "workout"),
        ("Заметки📃", "notes"),
        ("Установить напоминание📆", "reminder"),
        ("Сборник упражнений📕", "exercises"),
        ("Калории🍰", "calories"),
        ("Рецепты🍽️", "recipes")
    ]

    for text, callback_data in buttons:
        builder.button(text=text, callback_data=callback_data)

    builder.adjust(2, 2, 2, 1, 1, 1)  # Настройка расположения кнопок
    return builder.as_markup()


def get_workouts_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора тренировок"""
    builder = InlineKeyboardBuilder()

    workouts = [
        ("Силовая (Базовая)🦍", "strength"),
        ("Функциональная (Взрывная сила)🐂", "functional"),
        ("Оздоровительная (Для осанки)🦙", "wellness"),
        ("На Выносливость (Круговая)🐫", "endurance"),
        ("Для Пресса и Координации🦈", "for_press"),
        ("Нижняя Сила (Ноги и кор)🦩", "lower_strength"),
        ('Связка "Турник + Брусья"🐒', "combination"),
        ("Фулл-Бади (На все тело)🐊", "full_body"),
        ("Уличный Воркаут (Статика и динамика)🐆", "street_workout"),
        ("ВИИТ (Сжигание калорий)🐅", "calorie_burning")
    ]

    for text, callback_data in workouts:
        builder.button(text=text, callback_data=callback_data)

    builder.adjust(1)  # Все кнопки в один столбец
    return builder.as_markup()


def get_exercises_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа упражнений"""
    builder = InlineKeyboardBuilder()

    exercises = [
        ("На турнике", "horizontal"),
        ("На брусьях", "bars"),
        ("Без инвентаря", "inventory")
    ]

    for text, callback_data in exercises:
        builder.button(text=text, callback_data=callback_data)

    builder.adjust(1)
    return builder.as_markup()


def get_legends_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для историй Арни"""
    builder = InlineKeyboardBuilder()

    legends = [
        ("🍌 История 1: Рождение Стального Гориллы", "h1"),
        ("🍌x3 История 2: Первый поход в «Каменный Лес»", "h2"),
        ("🍌x5 История 3: Битва с Лентяй-Гориллой", "h3"),
        ("🍌x7 История 4: Секрет «Стройматериалов»", "h4"),
        ("🍌x10 История 5: Тайна «Умных Повторений»", "h5"),
        ("🍌x15 История 6: Война с Сахарным Демоном", "h6"),
        ("🍌x20 История 7: Союз с Сонным Йети", "h7"),
        ("🍌x30 История 8: Завоевание «Бетонных Джунглей»", "h8"),
        ("🍌x50 История 9: Философия «Баланса Жизни»", "h9"),
        ("🍌x100 История 10: Наследие Железного Гориллы", "h10")
    ]

    for text, callback_data in legends:
        builder.button(text=text, callback_data=callback_data)

    builder.adjust(1)
    return builder.as_markup()


def get_notes_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для работы с заметками"""
    builder = ReplyKeyboardBuilder()

    buttons = [
        "➕Добавить📌",
        "❌Удалить📌",
        "🗑️Очистить📌",
        "📋Список📌"
    ]

    for button in buttons:
        builder.button(text=button)

    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)


def get_reminders_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для работы с напоминаниями"""
    builder = ReplyKeyboardBuilder()

    buttons = [
        "➕Добавить⏰",
        "❌Удалить⏰",
        "📋Список⏰"
    ]

    for button in buttons:
        builder.button(text=button)

    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)


def get_calories_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для работы с калориями"""
    builder = ReplyKeyboardBuilder()

    buttons = [
        "Добавить ккал🍔",
        "Сжечь ккал🔥",
        "Обнулить ккал🔄"
    ]

    for button in buttons:
        builder.button(text=button)

    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)


def get_fitness_level_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора уровня подготовки"""
    builder = ReplyKeyboardBuilder()

    buttons = [
        "Начинающий🥉",
        "Продвинутый🥈",
        "Профессионал🥇"
    ]

    for button in buttons:
        builder.button(text=button)

    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)


def get_plot_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для историй Арнольда"""
    builder = ReplyKeyboardBuilder()

    buttons = [
        "Отметиться🍌",
        "Легенды Арни✨"
    ]

    for button in buttons:
        builder.button(text=button)

    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


# ====================== ОБРАБОТЧИКИ КОМАНД ======================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    user_name = message.from_user.first_name
    welcome = f"""{user_name}, Привет!
➣Меня зовут Арнольд🦍, я тебя приобщу к ЗОЖ (здоровому образу жизни).

➣Вноси свои физические данные в разделе "Изменить профиль⚙️" и выбирай тренировку по душе!

➣Открой /menu, что бы ознакомиться с функционалом.
    """
    await message.answer(welcome)


@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    """Обработчик команды /menu"""
    await message.answer(
        text='――――🦾Все функции бота!🗂――――',
        reply_markup=get_main_menu_keyboard()
    )


@dp.message(Command("notes"))
async def cmd_notes(message: types.Message):
    """Обработчик команды /notes"""
    await message.answer(
        "Я напомню нужные тебе события!",
        reply_markup=get_notes_keyboard()
    )


@dp.message(Command("reminders"))
async def cmd_reminders(message: types.Message):
    """Обработчик команды /reminders"""
    await message.answer(
        "Я напомню нужные тебе события!",
        reply_markup=get_reminders_keyboard()
    )


# ====================== ОБРАБОТЧИКИ CALLBACK-QUERY ======================

@dp.callback_query(F.data == "profile")
async def show_profile(callback: types.CallbackQuery):
    """Показать профиль пользователя"""
    user_id = callback.from_user.id
    profile = get_user_profile(user_id)

    name = callback.from_user.first_name
    weight = profile.get('weight', '🚫')
    height = profile.get('height', '🚫')
    age = profile.get('age', '🚫')
    calories = profile.get('calories', '🚫')
    day_calories = profile.get('day_calories', '🍰')
    fitness_level = profile.get('fitness_level', '🚫')
    bananas = profile.get('bananas', '🚫')

    level_display = {
        'beginner': 'Начинающий🥉',
        'intermediate': 'Продвинутый🥈',
        'advanced': 'Профессионал🥇'
    }.get(fitness_level, fitness_level)

    profile_text = f"""
🗿Ваш профиль:
┏Имя: {name}
┠Бананы: {bananas} 🍌
┠Вес: {weight} кг
┠Рост: {height} см
┠Возраст: {age} лет
┠Уровень: {level_display}
┗Дневная норма: {day_calories}/{calories} ккал
    """
    await callback.message.answer(profile_text)
    await callback.answer()


@dp.callback_query(F.data == "edit_profile")
async def edit_profile(callback: types.CallbackQuery, state: FSMContext):
    """Начать редактирование профиля"""
    await callback.message.answer(
        "Введите параметры в формате: вес рост возраст\nПример: 70 180 25"
    )
    await state.set_state(UserProfile.waiting_for_params)
    await callback.answer()


@dp.callback_query(F.data == "workout")
async def show_workouts(callback: types.CallbackQuery):
    """Показать список тренировок"""
    if not check_profile_exists(callback.from_user.id):
        await callback.message.answer(
            "❌ Сначала создайте профиль в разделе 'Изменить профиль⚙️'!"
        )
        await callback.answer()
        return

    await callback.message.answer(
        text='Готовые тренировки✅',
        reply_markup=get_workouts_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data.in_({
    "strength", "functional", "wellness", "endurance", "for_press",
    "lower_strength", "combination", "full_body", "street_workout",
    "calorie_burning"
}))
async def show_workout_detail(callback: types.CallbackQuery):
    """Показать детали тренировки"""
    user_id = callback.from_user.id

    # Получаем данные пользователя
    weight = get_user_field(user_id, 'weight', 70)
    height = get_user_field(user_id, 'height', 175)
    age = get_user_field(user_id, 'age', 25)
    fitness_level = get_user_field(user_id, 'fitness_level', 'beginner')

    # Маппинг тренировок
    workout_map = {
        "strength": {
            "name": "Силовая (Базовая)🦍",
            "goal": "Развитие максимальной силы.🏆",
            "rest": "90-120 секунд.⏱️",
            "hr_key": "Strength",
            "workout_type": "Strength",
            "exercises": [
                f"1.➣Подтягивания: 4 подхода по {ExerciseCalculator.calculate_pullups(weight, height, age, fitness_level)} раз",
                f"2.➣Отжимания на брусьях: 4 подхода по {ExerciseCalculator.calculate_dips(weight, height, age, fitness_level)} раз",
                f"3.➣Приседания: 4 подхода по {ExerciseCalculator.calculate_squats(weight, height, age, fitness_level)} раз",
                f"4.➣Планка (сек): 3 подхода по {ExerciseCalculator.calculate_plank(weight, height, age, fitness_level)} сек"
            ]
        },
        "functional": {
            "name": "Функциональная (Взрывная сила)🐂",
            "goal": "Развитие мощности.🏆",
            "rest": "60-75 секунд.⏱️",
            "hr_key": "Power",
            "workout_type": "Power",
            "exercises": [
                f"1.➣Подтягивания с усилием: 4 подхода по {ExerciseCalculator.calculate_pullups(weight, height, age, fitness_level)} раз",
                f"2.➣Отжимания на брусьях взрывные: 3 подхода по {ExerciseCalculator.calculate_dips(weight, height, age, fitness_level)} раз",
                f"3.➣Берпи: 3 подхода по {ExerciseCalculator.calculate_burpees(weight, height, age, fitness_level)} раз",
                f"4.➣Прыжки из приседа: 3 подхода по {ExerciseCalculator.calculate_jump_squats(weight, height, age, fitness_level)} раз"
            ]
        }
        # ... добавьте остальные тренировки по аналогии
    }

    workout = workout_map.get(callback.data)
    if not workout:
        await callback.answer("Тренировка не найдена")
        return

    # Получаем пульс и калории
    hr_data = HeartRateCalculator.get_all_workouts_hr(age)
    calories_burned = Calories.add_workout_calories(
        ExerciseCalculator.get_workout(
            workout["workout_type"], weight, height, age, fitness_level
        ),
        weight
    )

    # Формируем текст тренировки
    workout_text = f"""
Тренировка: {workout['name']}
Цель: {workout['goal']}
Отдых: {workout['rest']}
Рекомендуемый пульс: {hr_data.get(workout['hr_key'], 'N/A')}уд/мин❤️
Калории: {calories_burned}ккал.🍰

{chr(10).join(workout['exercises'])}
    """

    await callback.message.answer(workout_text)
    await callback.answer()


@dp.callback_query(F.data == "notes")
async def show_notes_help(callback: types.CallbackQuery):
    """Показать помощь по заметкам"""
    help_text = """
Используй команду:
/notes - заметки 
    """
    await callback.message.answer(help_text)
    await callback.answer()


@dp.callback_query(F.data == "reminder")
async def show_reminder_help(callback: types.CallbackQuery):
    """Показать помощь по напоминаниям"""
    help_text = """
Используй команду:
/reminders - напоминания
    """
    await callback.message.answer(help_text)
    await callback.answer()


@dp.callback_query(F.data == "exercises")
async def show_exercises(callback: types.CallbackQuery):
    """Показать сборник упражнений"""
    await callback.message.answer(
        text='Сборник упражнений📕',
        reply_markup=get_exercises_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data == "plot")
async def show_plot(callback: types.CallbackQuery):
    """Показать истории Арнольда"""
    await callback.message.answer(
        text='Истории Арнольда🦍',
        reply_markup=get_plot_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data == "calories")
async def show_calories_menu(callback: types.CallbackQuery):
    """Показать меню калорий"""
    if not check_profile_exists(callback.from_user.id):
        await callback.message.answer(
            "❌ Сначала создайте профиль в разделе 'Изменить профиль⚙️'!"
        )
        await callback.answer()
        return

    await callback.message.answer(
        text='Калории🍰',
        reply_markup=get_calories_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data == "recipes")
async def show_recipes(callback: types.CallbackQuery):
    """Показать рецепты"""
    text = '🍽️Рецепты, от которых ты не поправишься:\n http://propernutritionarnold.tilda.ws/'
    await callback.message.answer(text, disable_web_page_preview=True)
    await callback.answer()


@dp.callback_query(F.data.startswith("h"))
async def show_legend(callback: types.CallbackQuery):
    """Показать легенду Арни"""
    user_id = callback.from_user.id
    bananas = get_user_field(user_id, 'bananas', 0)

    # Проверяем стоимость каждой истории
    legend_cost = {
        "h1": 0,
        "h2": 2,
        "h3": 4,
        "h4": 6,
        "h5": 9,
        "h6": 14,
        "h7": 19,
        "h8": 29,
        "h9": 49,
        "h10": 99
    }

    required_bananas = legend_cost.get(callback.data, 0)

    if bananas < required_bananas:
        await callback.message.answer('У вас недостаточно бананов!🍌')
        await callback.answer()
        return

    # Здесь должен быть код для показа истории
    # Пока заглушка
    await callback.message.answer(f"История {callback.data} будет здесь")
    await callback.answer()


# ====================== ОБРАБОТЧИКИ СОСТОЯНИЙ ======================

@dp.message(UserProfile.waiting_for_params)
async def process_user_params(message: types.Message, state: FSMContext):
    """Обработка введенных параметров пользователя"""
    try:
        parts = message.text.split()
        if len(parts) != 3:
            raise ValueError

        weight = int(parts[0])
        height = int(parts[1])
        age = int(parts[2])

        # Сохраняем базовые данные
        user_profile = {
            'name': message.from_user.first_name,
            'weight': weight,
            'height': height,
            'age': age,
            'fitness_level': 'beginner',
            'calories': Calories.calculate_daily_norm(weight, height, age, 'beginner'),
            'day_calories': 0,
            'bananas': 0
        }

        save_user_profile(message.from_user.id, user_profile)

        await message.answer(
            f"✅ Данные сохранены!\nВес: {weight}кг\nРост: {height}см\nВозраст: {age}лет\n\n"
            "Теперь выбери уровень подготовки!💪",
            reply_markup=get_fitness_level_keyboard()
        )

        await state.set_state(UserProfile.waiting_for_fitness_level)

    except ValueError:
        await message.answer(
            "❌ Ошибка формата! Используйте цифры в формате: 'вес рост возраст'\nПример: 70 180 25"
        )


@dp.message(UserProfile.waiting_for_fitness_level)
async def process_fitness_level(message: types.Message, state: FSMContext):
    """Обработка выбора уровня подготовки"""
    level_map = {
        "Начинающий🥉": "beginner",
        "Продвинутый🥈": "intermediate",
        "Профессионал🥇": "advanced"
    }

    level = level_map.get(message.text)
    if level:
        update_user_field(message.from_user.id, 'fitness_level', level)
        FitnessCoefficient.fitness_level = level

        level_display = {
            'beginner': 'Начинающий🥉',
            'intermediate': 'Продвинутый🥈',
            'advanced': 'Профессионал🥇'
        }.get(level, level)

        await message.answer(
            f"✅ {level_display} уровень подготовки сохранён!\nМожете вернуться в /menu"
        )
        await state.clear()
    else:
        await message.answer(
            "Пожалуйста, выбери уровень из предложенных вариантов",
            reply_markup=get_fitness_level_keyboard()
        )


# ====================== ОБРАБОТЧИКИ ЗАМЕТОК ======================

@dp.message(F.text == "➕Добавить📌")
async def add_note_start(message: types.Message, state: FSMContext):
    """Начать добавление заметки"""
    await message.answer("📝 Напиши текст заметки:")
    await state.set_state(NoteStates.waiting_for_note_text)


@dp.message(NoteStates.waiting_for_note_text)
async def add_note_process(message: types.Message, state: FSMContext):
    """Обработать добавление заметки"""
    note_text = message.text
    user_id = message.from_user.id

    notes = load_json_file(NOTES_FILE)
    if user_id not in notes:
        notes[user_id] = {}

    note_id = len(notes[user_id]) + 1
    notes[user_id][note_id] = note_text

    save_json_file(NOTES_FILE, notes)

    await message.answer(f"✅ Заметка #{note_id} сохранена!")
    await state.clear()


@dp.message(F.text == "📋Список📌")
async def list_notes(message: types.Message):
    """Показать список заметок"""
    user_id = message.from_user.id
    notes = load_json_file(NOTES_FILE)

    user_notes = notes.get(user_id, {})

    if not user_notes:
        await message.answer("📭 У тебя пока нет заметок")
        return

    response = "📋 Твои заметки:\n\n"
    for note_id, note_text in user_notes.items():
        response += f"#{note_id}: {note_text}\n\n"

    await message.answer(response)


@dp.message(F.text == "❌Удалить📌")
async def delete_note_start(message: types.Message, state: FSMContext):
    """Начать удаление заметки"""
    user_id = message.from_user.id
    notes = load_json_file(NOTES_FILE)

    user_notes = notes.get(user_id, {})

    if not user_notes:
        await message.answer("📭 Нечего удалять - заметок нет")
        return

    response = "❌ Какое заметку удалить? Напиши номер:\n\n"
    for note_id, note_text in user_notes.items():
        response += f"#{note_id}: {note_text}\n"

    await message.answer(response)
    await state.set_state(NoteStates.waiting_for_note_delete)


@dp.message(NoteStates.waiting_for_note_delete)
async def delete_note_process(message: types.Message, state: FSMContext):
    """Обработать удаление заметки"""
    try:
        note_id = int(message.text)
        user_id = message.from_user.id

        notes = load_json_file(NOTES_FILE)
        user_notes = notes.get(user_id, {})

        if note_id in user_notes:
            del notes[user_id][note_id]
            notes[user_id] = renumber_notes(notes[user_id])

            save_json_file(NOTES_FILE, notes)
            await message.answer(f"✅ Заметка #{note_id} удалена")
        else:
            await message.answer(f"⚠️ Заметка #{note_id} не найдена!")

        await state.clear()

    except ValueError:
        await message.answer("❌ Напиши номер заметки цифрой")


@dp.message(F.text == "🗑️Очистить📌")
async def clear_notes(message: types.Message):
    """Очистить все заметки"""
    user_id = message.from_user.id
    notes = load_json_file(NOTES_FILE)

    if user_id in notes and notes[user_id]:
        notes[user_id] = {}
        save_json_file(NOTES_FILE, notes)
        await message.answer("🗑️ Все заметки удалены!")
    else:
        await message.answer("📭 Нечего удалять - заметок нет")


# ====================== ОБРАБОТЧИКИ НАПОМИНАНИЙ ======================

@dp.message(F.text == "➕Добавить⏰")
async def add_reminder_start(message: types.Message, state: FSMContext):
    """Начать добавление напоминания"""
    await message.answer(
        "Введите день и время в формате:\n'понедельник 14:30 Напоминание'"
    )
    await state.set_state(ReminderStates.waiting_for_reminder)


@dp.message(ReminderStates.waiting_for_reminder)
async def add_reminder_process(message: types.Message, state: FSMContext):
    """Обработать добавление напоминания"""
    try:
        parts = message.text.split(' ', 2)
        if len(parts) != 3:
            raise ValueError

        day = parts[0].lower()
        time_str = parts[1]
        text = parts[2]

        days = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
        if day not in days:
            await message.answer("Ошибка в дне недели!")
            return

        # Проверяем время
        datetime.strptime(time_str, '%H:%M')

        # Сохраняем в памяти
        user_id = message.from_user.id
        if user_id not in user_reminders:
            user_reminders[user_id] = []

        user_reminders[user_id].append({
            'day': day,
            'time': time_str,
            'text': text
        })

        await message.answer(f"✅ Добавлено: {day} в {time_str}")
        await state.clear()

    except ValueError:
        await message.answer("Ошибка формата! Используйте: 'понедельник 14:30 Текст'")
    except Exception:
        await message.answer("Ошибка при обработке напоминания")


@dp.message(F.text == "📋Список⏰")
async def list_reminders(message: types.Message):
    """Показать список напоминаний"""
    user_id = message.from_user.id

    if user_id not in user_reminders or not user_reminders[user_id]:
        await message.answer("Нет напоминаний")
        return

    text = "Ваши напоминания:\n\n"
    for i, rem in enumerate(user_reminders[user_id], 1):
        text += f"{i}. {rem['day']} {rem['time']} - {rem['text']}\n"

    await message.answer(text)


@dp.message(F.text == "❌Удалить⏰")
async def delete_reminder_start(message: types.Message, state: FSMContext):
    """Начать удаление напоминания"""
    user_id = message.from_user.id

    if user_id not in user_reminders or not user_reminders[user_id]:
        await message.answer("Нет напоминаний для удаления")
        return

    await message.answer("Введите номер напоминания для удаления:")
    await state.set_state(ReminderStates.waiting_for_reminder_delete)


@dp.message(ReminderStates.waiting_for_reminder_delete)
async def delete_reminder_process(message: types.Message, state: FSMContext):
    """Обработать удаление напоминания"""
    try:
        num = int(message.text) - 1
        user_id = message.from_user.id

        if 0 <= num < len(user_reminders[user_id]):
            user_reminders[user_id].pop(num)
            await message.answer("✅ Удалено!")
        else:
            await message.answer("Неверный номер!")

        await state.clear()

    except ValueError:
        await message.answer("Ошибка! Введите номер цифрой")


# ====================== ОБРАБОТЧИКИ КАЛОРИЙ ======================

@dp.message(F.text == "Добавить ккал🍔")
async def add_calories_start(message: types.Message, state: FSMContext):
    """Начать добавление калорий"""
    if not check_profile_exists(message.from_user.id):
        await message.answer("❌ Сначала создайте профиль в разделе 'Изменить профиль⚙️'!")
        return

    await message.answer(
        "🍔Введите калорийность продукта на 100г и через пробел массу продукта.\nПример: 150 52"
    )
    await state.set_state(CalorieStates.waiting_for_calories_add)


@dp.message(CalorieStates.waiting_for_calories_add)
async def add_calories_process(message: types.Message, state: FSMContext):
    """Обработать добавление калорий"""
    try:
        parts = message.text.split()
        if len(parts) != 2:
            raise ValueError

        calories_per_100g = int(parts[0])
        weight_in_grams = int(parts[1])

        calories_to_add = Calories.calculate_calories(calories_per_100g, weight_in_grams)
        user_id = message.from_user.id

        day_calories = get_user_field(user_id, 'day_calories', 0)
        new_calories = day_calories + calories_to_add

        update_user_field(user_id, 'day_calories', new_calories)

        await message.answer(