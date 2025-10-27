from Profile import FitnessCoefficient


class ExerciseCalculator:
    # Базовые значения упражнений для человека 70 кг, 25 лет, intermediate
    BASE_EXERCISES = {
        # Турник
        "pullups": 8,  # Подтягивания
        "hang_time": 30,  # Вис на турнике (секунды)
        "leg_raises": 12,  # Подъем ног в висе

        # Брусья
        "dips": 10,  # Отжимания на брусьях
        "l_sit": 20,  # Уголок на брусьях (секунды)
        "front_support": 30,  # Передний вис на брусьях (секунды)

        # Без инвентаря
        "squats": 20,  # Приседания
        "pistol_squats": 5,  # Приседания на одной ноге
        "lunges": 15,  # Выпады
        "jump_squats": 12,  # Прыжки из приседа
        "burpees": 8,  # Берпи
        "pushups": 15,  # Отжимания от пола
        "plank": 45,  # Планка (секунды)
        "crunches": 25,  # Скручивания
        "bicycle": 30  # Велосипед (секунды)
    }

    # Турник
    @staticmethod
    def calculate_pullups():
        coefficient = FitnessCoefficient.calculate_coefficient()
        return max(3, min(20, int(ExerciseCalculator.BASE_EXERCISES["pullups"] * coefficient)))

    @staticmethod
    def calculate_hang_time():
        coefficient = FitnessCoefficient.calculate_coefficient()
        return max(15, min(120, int(ExerciseCalculator.BASE_EXERCISES["hang_time"] * coefficient)))

    @staticmethod
    def calculate_leg_raises():
        coefficient = FitnessCoefficient.calculate_coefficient()
        return max(5, min(25, int(ExerciseCalculator.BASE_EXERCISES["leg_raises"] * coefficient)))

    # Брусья
    @staticmethod
    def calculate_dips():
        coefficient = FitnessCoefficient.calculate_coefficient()
        return max(5, min(25, int(ExerciseCalculator.BASE_EXERCISES["dips"] * coefficient)))

    @staticmethod
    def calculate_l_sit():
        coefficient = FitnessCoefficient.calculate_coefficient()
        return max(10, min(60, int(ExerciseCalculator.BASE_EXERCISES["l_sit"] * coefficient)))

    @staticmethod
    def calculate_front_support():
        coefficient = FitnessCoefficient.calculate_coefficient()
        return max(15, min(90, int(ExerciseCalculator.BASE_EXERCISES["front_support"] * coefficient)))

    # Без инвентаря
    @staticmethod
    def calculate_squats():
        coefficient = FitnessCoefficient.calculate_coefficient()
        return max(10, min(50, int(ExerciseCalculator.BASE_EXERCISES["squats"] * coefficient)))

    @staticmethod
    def calculate_pistol_squats():
        coefficient = FitnessCoefficient.calculate_coefficient()
        return max(3, min(15, int(ExerciseCalculator.BASE_EXERCISES["pistol_squats"] * coefficient)))

    @staticmethod
    def calculate_lunges():
        coefficient = FitnessCoefficient.calculate_coefficient()
        return max(8, min(30, int(ExerciseCalculator.BASE_EXERCISES["lunges"] * coefficient)))

    @staticmethod
    def calculate_jump_squats():
        coefficient = FitnessCoefficient.calculate_coefficient()
        return max(5, min(25, int(ExerciseCalculator.BASE_EXERCISES["jump_squats"] * coefficient)))

    @staticmethod
    def calculate_burpees():
        coefficient = FitnessCoefficient.calculate_coefficient()
        return max(5, min(20, int(ExerciseCalculator.BASE_EXERCISES["burpees"] * coefficient)))

    @staticmethod
    def calculate_pushups():
        coefficient = FitnessCoefficient.calculate_coefficient()
        return max(5, min(30, int(ExerciseCalculator.BASE_EXERCISES["pushups"] * coefficient)))

    @staticmethod
    def calculate_plank():
        coefficient = FitnessCoefficient.calculate_coefficient()
        return max(20, min(180, int(ExerciseCalculator.BASE_EXERCISES["plank"] * coefficient)))

    @staticmethod
    def calculate_crunches():
        coefficient = FitnessCoefficient.calculate_coefficient()
        return max(10, min(50, int(ExerciseCalculator.BASE_EXERCISES["crunches"] * coefficient)))

    @staticmethod
    def calculate_bicycle():
        coefficient = FitnessCoefficient.calculate_coefficient()
        return max(20, min(90, int(ExerciseCalculator.BASE_EXERCISES["bicycle"] * coefficient)))

    @staticmethod
    def get_recommended_workout():
        """Получить всю рекомендованную тренировку"""
        return {
            # Турник
            "Подтягивания": ExerciseCalculator.calculate_pullups(),
            "Вис на турнике (сек)": ExerciseCalculator.calculate_hang_time(),
            "Подъем ног в висе": ExerciseCalculator.calculate_leg_raises(),

            # Брусья
            "Отжимания на брусьях": ExerciseCalculator.calculate_dips(),
            "Уголок на брусьях (сек)": ExerciseCalculator.calculate_l_sit(),
            "Передний вис на брусьях (сек)": ExerciseCalculator.calculate_front_support(),

            # Без инвентаря
            "Приседания": ExerciseCalculator.calculate_squats(),
            "Приседания на одной ноге": ExerciseCalculator.calculate_pistol_squats(),
            "Выпады": ExerciseCalculator.calculate_lunges(),
            "Прыжки из приседа": ExerciseCalculator.calculate_jump_squats(),
            "Берпи": ExerciseCalculator.calculate_burpees(),
            "Отжимания от пола": ExerciseCalculator.calculate_pushups(),
            "Планка (сек)": ExerciseCalculator.calculate_plank(),
            "Скручивания": ExerciseCalculator.calculate_crunches(),
            "Велосипед (сек)": ExerciseCalculator.calculate_bicycle()
        }

    @staticmethod
    def get_workout(workout):
        if workout == "Strength":
            return {
                "Подтягивания": ExerciseCalculator.calculate_pullups() * 4,
                "Отжимания на брусьях": ExerciseCalculator.calculate_dips() * 4,
                "Приседания": ExerciseCalculator.calculate_squats() * 4,
                "Планка (сек)": ExerciseCalculator.calculate_plank() * 3
            }
        if workout == "Power":
            return {
                "Подтягивания": ExerciseCalculator.calculate_pullups() * 4,
                "Отжимания на брусьях": ExerciseCalculator.calculate_dips() * 3,
                "Берпи": ExerciseCalculator.calculate_burpees() * 3,
                "Прыжки из приседа": ExerciseCalculator.calculate_jump_squats() * 3
            }
        if workout == "Posture":
            return {
                "Вис на турнике (сек)": ExerciseCalculator.calculate_hang_time() * 3,
                "Подъем ног в висе": ExerciseCalculator.calculate_leg_raises() * 3,
                "Отжимания на брусьях": ExerciseCalculator.calculate_dips() * 3,
                "Планка (сек)": ExerciseCalculator.calculate_plank() * 3
            }
        if workout == "Endurance":
            return {
                "Подтягивания": ExerciseCalculator.calculate_pullups() * 5,
                "Отжимания на брусьях": ExerciseCalculator.calculate_dips() * 5,
                "Приседания": ExerciseCalculator.calculate_squats() * 5,
                "Берпи": ExerciseCalculator.calculate_burpees() * 5
            }
        if workout == "Core":
            return {
                "Подъем ног в висе": ExerciseCalculator.calculate_leg_raises() * 4,
                "Уголок на брусьях": ExerciseCalculator.calculate_l_sit() * 3,
                "Скручивания": ExerciseCalculator.calculate_crunches() * 3,
                "Велосипед": ExerciseCalculator.calculate_bicycle() * 3
            }
        if workout == "Lower":
            return {
                "Приседания на одной ноге": ExerciseCalculator.calculate_pistol_squats() * 4,
                "Прыжки из приседа": ExerciseCalculator.calculate_jump_squats() * 3,
                "Подъем ног в висе": ExerciseCalculator.calculate_leg_raises() * 3,
                "Выпады": ExerciseCalculator.calculate_lunges() * 3
            }
        if workout == "Superset":
            return {
                "Подтягивания": ExerciseCalculator.calculate_pullups() * 4,
                "Отжимания на брусьях": ExerciseCalculator.calculate_dips() * 4,
                "Подъем ног в висе": ExerciseCalculator.calculate_leg_raises() * 3,
                "Отжимания от пола": ExerciseCalculator.calculate_pushups() * 3
            }
        if workout == "Full-Body":
            return {
                "Подтягивания": ExerciseCalculator.calculate_pullups() * 3,
                "Отжимания на брусьях": ExerciseCalculator.calculate_dips() * 3,
                "Приседания": ExerciseCalculator.calculate_squats() * 3,
                "Подъем ног в висе": ExerciseCalculator.calculate_leg_raises() * 3
            }
        if workout == "Street":
            return {
                "Подтягивания": ExerciseCalculator.calculate_pullups() * 3,
                "Передний вис на брусьях":  ExerciseCalculator.calculate_front_support() * 3,
                "Отжимания на брусьях": ExerciseCalculator.calculate_dips() * 3,
                "Уголок на брусьях": ExerciseCalculator.calculate_l_sit() * 3
            }
        if workout == "HIIT":
            return {
                "Берпи": ExerciseCalculator.calculate_burpees() * 5,
                "Подтягивания":  ExerciseCalculator.calculate_pullups() * 5,
                "Отжимания на брусьях": ExerciseCalculator.calculate_dips() * 5,
                "Прыжки из приседа": ExerciseCalculator.calculate_l_sit() * 5
            }




