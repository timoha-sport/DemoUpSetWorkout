class FitnessCoefficient:
    # Поля класса (общие для всех)
    weight = 70
    height = 180
    age = 25
    fitness_level = "beginner"

    @staticmethod
    def calculate_bmi():
        """Рассчитать ИМТ"""
        height_m = FitnessCoefficient.height / 100
        return FitnessCoefficient.weight / (height_m ** 2)

    @staticmethod
    def get_fitness_multiplier():
        """Множитель уровня подготовки"""
        multipliers = {
            "beginner": 0.7,
            "intermediate": 1.0,
            "advanced": 1.3
        }
        return multipliers.get(FitnessCoefficient.fitness_level, 1.0)

    @staticmethod
    def get_age_factor():
        """Фактор возраста"""
        if FitnessCoefficient.age < 25:
            return 1.2
        elif FitnessCoefficient.age < 40:
            return 1.0
        elif FitnessCoefficient.age < 55:
            return 0.9
        else:
            return 0.8

    @staticmethod
    def get_bmi_factor():
        """Фактор ИМТ"""
        bmi = FitnessCoefficient.calculate_bmi()
        if bmi < 18.5:
            return 0.8
        elif bmi < 25:
            return 1.0
        elif bmi < 30:
            return 1.2
        else:
            return 1.1

    @staticmethod
    def get_weight_factor():
        """Фактор веса (для отжиманий)"""
        base_weight = 70
        return max(0.7, min(1.3, base_weight / FitnessCoefficient.weight))

    @staticmethod
    def calculate_coefficient():
        """Общий коэффициент подготовки"""
        fitness = FitnessCoefficient.get_fitness_multiplier()
        age = FitnessCoefficient.get_age_factor()
        bmi = FitnessCoefficient.get_bmi_factor()
        weight = FitnessCoefficient.get_weight_factor()

        # Среднее значение всех факторов
        return (fitness + age + bmi + weight) / 4