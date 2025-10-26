import datetime


class Calories:
    # Поля класса
    daily_calories = 0
    last_reset_date = datetime.date.today()

    # Статические константы
    CALORIES_PER_EXERCISE = {
        # Турник
        "Подтягивания": 0.8,
        "Вис на турнике (сек)": 0.02,  # за секунду
        "Подъем ног в висе": 0.5,

        # Брусья
        "Отжимания на брусьях": 0.7,
        "Уголок на брусьях (сек)": 0.03,
        "Передний вис на брусьях (сек)": 0.02,

        # Без инвентаря
        "Приседания": 0.4,
        "Приседания на одной ноге": 0.6,
        "Выпады": 0.3,
        "Прыжки из приседа": 0.7,
        "Берпи": 1.0,
        "Отжимания от пола": 0.5,
        "Планка (сек)": 0.015,
        "Скручивания": 0.2,
        "Велосипед (сек)": 0.025
    }

    @staticmethod
    def _reset_if_new_day():
        """Обнулить счетчик если наступил новый день"""
        today = datetime.date.today()
        if today > Calories.last_reset_date:
            Calories.daily_calories = 0
            Calories.last_reset_date = today

    @staticmethod
    def calculate_daily_norm(weight, height, age, activity_level="medium"):
        """
        Рассчитать дневную норму калорий
        activity_level: "low", "medium", "high"
        """
        # Базальный метаболизм (формула Миффлина-Сан Жеора)
        if age <= 0:
            age = 25  # защита от некорректного возраста

        # Базовый метаболизм
        if height > 100:  # если рост в см, переводим в метры для формулы
            height_m = height / 100
        else:
            height_m = height

        bmr = 10 * weight + 6.25 * (height_m * 100) - 5 * age + 5

        # Умножаем на коэффициент активности
        activity_multipliers = {
            "low": 1.2,  # сидячий образ жизни
            "medium": 1.55,  # умеренная активность
            "high": 1.725  # высокая активность
        }

        multiplier = activity_multipliers.get(activity_level, 1.55)
        daily_norm = bmr * multiplier

        return int(daily_norm)

    @staticmethod
    def calculate_exercise_calories(exercise_name, count, weight):
        """Рассчитать калории для конкретного упражнения"""
        if exercise_name not in Calories.CALORIES_PER_EXERCISE:
            return 0

        base_calories = Calories.CALORIES_PER_EXERCISE[exercise_name]

        # Корректируем на вес (чем больше вес, тем больше калорий сжигается)
        weight_factor = weight / 70  # базовый вес 70 кг

        # Для временных упражнений (секунды)
        if "сек" in exercise_name:
            calories = base_calories * count * weight_factor
        else:
            # Для упражнений на повторения
            calories = base_calories * count * weight_factor

        return round(calories, 1)

    @staticmethod
    def add_workout_calories(workout_data, weight):
        """
        Добавить калории от тренировки в дневной счетчик
        workout_data: словарь {упражнение: количество}
        weight: вес пользователя в кг
        """
        Calories._reset_if_new_day()

        total_workout_calories = 0

        for exercise, count in workout_data.items():
            if count > 0:  # считаем только если были выполнены упражнения
                exercise_calories = Calories.calculate_exercise_calories(exercise, count, weight)
                total_workout_calories += exercise_calories

        Calories.daily_calories += total_workout_calories
        return round(total_workout_calories, 1)

    @staticmethod
    def add_food_calories(calories):
        """Добавить калории от еды"""
        Calories._reset_if_new_day()
        Calories.daily_calories += calories

    @staticmethod
    def get_remaining_calories(weight, height, age, activity_level="medium"):
        """Получить оставшиеся калории на сегодня"""
        Calories._reset_if_new_day()

        daily_norm = Calories.calculate_daily_norm(weight, height, age, activity_level)
        remaining = daily_norm - Calories.daily_calories

        return {
            "daily_norm": daily_norm,
            "consumed": round(Calories.daily_calories, 1),
            "remaining": round(remaining, 1),
            "is_deficit": remaining > 0
        }

    @staticmethod
    def get_daily_stats():
        """Получить текущую статистику за день"""
        Calories._reset_if_new_day()
        return {
            "date": Calories.last_reset_date,
            "total_calories": round(Calories.daily_calories, 1)
        }

    @staticmethod
    def reset_manual():
        """Принудительно обнулить счетчик (для тестов)"""
        Calories.daily_calories = 0
        Calories.last_reset_date = datetime.date.today()