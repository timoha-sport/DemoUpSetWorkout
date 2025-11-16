class ExerciseCalculator:

    @staticmethod
    def calculate_pullups(weight, height, age, fitness_level):
        """Подтягивания - зависит от веса и уровня подготовки"""
        base = 8
        # Чем больше вес, тем меньше подтягиваний
        weight_factor = max(0.5, 1 - (weight - 70) / 100)
        # Уровень подготовки
        level_factor = {'beginner': 0.6, 'intermediate': 1.0, 'advanced': 1.4}.get(fitness_level, 1.0)
        return max(3, min(20, int(base * weight_factor * level_factor)))

    @staticmethod
    def calculate_hang_time(weight, height, age, fitness_level):
        """Вис на турнике - зависит от веса и возраста"""
        base = 30
        # Чем больше вес, тем сложнее висеть
        weight_factor = max(0.6, 1 - (weight - 70) / 150)
        # С возрастом выносливость снижается
        age_factor = 1.0 if age <= 40 else 0.8
        return max(15, min(120, int(base * weight_factor * age_factor)))

    @staticmethod
    def calculate_leg_raises(weight, height, age, fitness_level):
        """Подъем ног в висе - зависит от веса и уровня"""
        base = 12
        weight_factor = max(0.7, 1 - (weight - 70) / 120)
        level_factor = {'beginner': 0.7, 'intermediate': 1.0, 'advanced': 1.3}.get(fitness_level, 1.0)
        return max(5, min(25, int(base * weight_factor * level_factor)))

    @staticmethod
    def calculate_dips(weight, height, age, fitness_level):
        """Отжимания на брусьях - сильно зависит от веса"""
        base = 10
        weight_factor = max(0.4, 1 - (weight - 70) / 80)
        level_factor = {'beginner': 0.6, 'intermediate': 1.0, 'advanced': 1.4}.get(fitness_level, 1.0)
        return max(5, min(25, int(base * weight_factor * level_factor)))

    @staticmethod
    def calculate_l_sit(weight, height, age, fitness_level):
        """Уголок на брусьях - зависит от веса и силы кора"""
        base = 20
        weight_factor = max(0.5, 1 - (weight - 70) / 100)
        level_factor = {'beginner': 0.5, 'intermediate': 1.0, 'advanced': 1.5}.get(fitness_level, 1.0)
        return max(10, min(60, int(base * weight_factor * level_factor)))

    @staticmethod
    def calculate_front_support(weight, height, age, fitness_level):
        """Передний вис на брусьях"""
        base = 30
        weight_factor = max(0.6, 1 - (weight - 70) / 120)
        level_factor = {'beginner': 0.6, 'intermediate': 1.0, 'advanced': 1.4}.get(fitness_level, 1.0)
        return max(15, min(90, int(base * weight_factor * level_factor)))

    @staticmethod
    def calculate_squats(weight, height, age, fitness_level):
        """Приседания - меньше зависит от веса"""
        base = 20
        # Приседания проще для тяжелых людей
        weight_factor = min(1.2, 1 + (weight - 70) / 200)
        level_factor = {'beginner': 0.8, 'intermediate': 1.0, 'advanced': 1.2}.get(fitness_level, 1.0)
        return max(10, min(50, int(base * weight_factor * level_factor)))

    @staticmethod
    def calculate_pistol_squats(weight, height, age, fitness_level):
        """Приседания на одной ноге - сложное упражнение"""
        base = 5
        weight_factor = max(0.3, 1 - (weight - 70) / 60)
        level_factor = {'beginner': 0.4, 'intermediate': 1.0, 'advanced': 1.6}.get(fitness_level, 1.0)
        return max(3, min(15, int(base * weight_factor * level_factor)))

    @staticmethod
    def calculate_lunges(weight, height, age, fitness_level):
        """Выпады"""
        base = 15
        weight_factor = min(1.1, 1 + (weight - 70) / 150)
        level_factor = {'beginner': 0.8, 'intermediate': 1.0, 'advanced': 1.2}.get(fitness_level, 1.0)
        return max(8, min(30, int(base * weight_factor * level_factor)))

    @staticmethod
    def calculate_jump_squats(weight, height, age, fitness_level):
        """Прыжки из приседа - зависит от веса и возраста"""
        base = 12
        weight_factor = max(0.5, 1 - (weight - 70) / 80)
        age_factor = 1.0 if age <= 35 else 0.8
        level_factor = {'beginner': 0.7, 'intermediate': 1.0, 'advanced': 1.3}.get(fitness_level, 1.0)
        return max(5, min(25, int(base * weight_factor * age_factor * level_factor)))

    @staticmethod
    def calculate_burpees(weight, height, age, fitness_level):
        """Берпи - комплексное упражнение"""
        base = 8
        weight_factor = max(0.6, 1 - (weight - 70) / 100)
        level_factor = {'beginner': 0.6, 'intermediate': 1.0, 'advanced': 1.4}.get(fitness_level, 1.0)
        return max(5, min(20, int(base * weight_factor * level_factor)))

    @staticmethod
    def calculate_pushups(weight, height, age, fitness_level):
        """Отжимания от пола"""
        base = 15
        weight_factor = max(0.7, 1 - (weight - 70) / 130)
        level_factor = {'beginner': 0.7, 'intermediate': 1.0, 'advanced': 1.3}.get(fitness_level, 1.0)
        return max(5, min(30, int(base * weight_factor * level_factor)))

    @staticmethod
    def calculate_plank(weight, height, age, fitness_level):
        """Планка"""
        base = 45
        weight_factor = max(0.8, 1 - (weight - 70) / 150)
        level_factor = {'beginner': 0.7, 'intermediate': 1.0, 'advanced': 1.3}.get(fitness_level, 1.0)
        return max(20, min(180, int(base * weight_factor * level_factor)))

    @staticmethod
    def calculate_crunches(weight, height, age, fitness_level):
        """Скручивания"""
        base = 25
        weight_factor = max(0.8, 1 - (weight - 70) / 200)
        level_factor = {'beginner': 0.8, 'intermediate': 1.0, 'advanced': 1.2}.get(fitness_level, 1.0)
        return max(10, min(50, int(base * weight_factor * level_factor)))

    @staticmethod
    def calculate_bicycle(weight, height, age, fitness_level):
        """Велосипед"""
        base = 30
        weight_factor = max(0.8, 1 - (weight - 70) / 180)
        level_factor = {'beginner': 0.8, 'intermediate': 1.0, 'advanced': 1.2}.get(fitness_level, 1.0)
        return max(20, min(90, int(base * weight_factor * level_factor)))

    @staticmethod
    def get_workout(workout, weight, height, age, fitness_level):
        if workout == "Strength":
            return {
                "Подтягивания": ExerciseCalculator.calculate_pullups(weight, height, age, fitness_level) * 4,
                "Отжимания на брусьях": ExerciseCalculator.calculate_dips(weight, height, age, fitness_level) * 4,
                "Приседания": ExerciseCalculator.calculate_squats(weight, height, age, fitness_level) * 4,
                "Планка (сек)": ExerciseCalculator.calculate_plank(weight, height, age, fitness_level) * 3
            }
        if workout == "Power":
            return {
                "Подтягивания": ExerciseCalculator.calculate_pullups(weight, height, age, fitness_level) * 4,
                "Отжимания на брусьях": ExerciseCalculator.calculate_dips(weight, height, age, fitness_level) * 3,
                "Берпи": ExerciseCalculator.calculate_burpees(weight, height, age, fitness_level) * 3,
                "Прыжки из приседа": ExerciseCalculator.calculate_jump_squats(weight, height, age, fitness_level) * 3
            }
        if workout == "Posture":
            return {
                "Вис на турнике (сек)": ExerciseCalculator.calculate_hang_time(weight, height, age, fitness_level) * 3,
                "Подъем ног в висе": ExerciseCalculator.calculate_leg_raises(weight, height, age, fitness_level) * 3,
                "Отжимания на брусьях": ExerciseCalculator.calculate_dips(weight, height, age, fitness_level) * 3,
                "Планка (сек)": ExerciseCalculator.calculate_plank(weight, height, age, fitness_level) * 3
            }
        if workout == "Endurance":
            return {
                "Подтягивания": ExerciseCalculator.calculate_pullups(weight, height, age, fitness_level) * 5,
                "Отжимания на брусьях": ExerciseCalculator.calculate_dips(weight, height, age, fitness_level) * 5,
                "Приседания": ExerciseCalculator.calculate_squats(weight, height, age, fitness_level) * 5,
                "Берпи": ExerciseCalculator.calculate_burpees(weight, height, age, fitness_level) * 5
            }
        if workout == "Core":
            return {
                "Подъем ног в висе": ExerciseCalculator.calculate_leg_raises(weight, height, age, fitness_level) * 4,
                "Уголок на брусьях": ExerciseCalculator.calculate_l_sit(weight, height, age, fitness_level) * 3,
                "Скручивания": ExerciseCalculator.calculate_crunches(weight, height, age, fitness_level) * 3,
                "Велосипед": ExerciseCalculator.calculate_bicycle(weight, height, age, fitness_level) * 3
            }
        if workout == "Lower":
            return {
                "Приседания на одной ноге": ExerciseCalculator.calculate_pistol_squats(weight, height, age, fitness_level) * 4,
                "Прыжки из приседа": ExerciseCalculator.calculate_jump_squats(weight, height, age, fitness_level) * 3,
                "Подъем ног в висе": ExerciseCalculator.calculate_leg_raises(weight, height, age, fitness_level) * 3,
                "Выпады": ExerciseCalculator.calculate_lunges(weight, height, age, fitness_level) * 3
            }
        if workout == "Superset":
            return {
                "Подтягивания": ExerciseCalculator.calculate_pullups(weight, height, age, fitness_level) * 4,
                "Отжимания на брусьях": ExerciseCalculator.calculate_dips(weight, height, age, fitness_level) * 4,
                "Подъем ног в висе": ExerciseCalculator.calculate_leg_raises(weight, height, age, fitness_level) * 3,
                "Отжимания от пола": ExerciseCalculator.calculate_pushups(weight, height, age, fitness_level) * 3
            }
        if workout == "Full-Body":
            return {
                "Подтягивания": ExerciseCalculator.calculate_pullups(weight, height, age, fitness_level) * 3,
                "Отжимания на брусьях": ExerciseCalculator.calculate_dips(weight, height, age, fitness_level) * 3,
                "Приседания": ExerciseCalculator.calculate_squats(weight, height, age, fitness_level) * 3,
                "Подъем ног в висе": ExerciseCalculator.calculate_leg_raises(weight, height, age, fitness_level) * 3
            }
        if workout == "Street":
            return {
                "Подтягивания": ExerciseCalculator.calculate_pullups(weight, height, age, fitness_level) * 3,
                "Передний вис на брусьях": ExerciseCalculator.calculate_front_support(weight, height, age, fitness_level) * 3,
                "Отжимания на брусьях": ExerciseCalculator.calculate_dips(weight, height, age, fitness_level) * 3,
                "Уголок на брусьях": ExerciseCalculator.calculate_l_sit(weight, height, age, fitness_level) * 3
            }
        if workout == "HIIT":
            return {
                "Берпи": ExerciseCalculator.calculate_burpees(weight, height, age, fitness_level) * 5,
                "Подтягивания": ExerciseCalculator.calculate_pullups(weight, height, age, fitness_level) * 5,
                "Отжимания на брусьях": ExerciseCalculator.calculate_dips(weight, height, age, fitness_level) * 5,
                "Прыжки из приседа": ExerciseCalculator.calculate_l_sit(weight, height, age, fitness_level) * 5
            }