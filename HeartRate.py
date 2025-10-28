class HeartRateCalculator:
    """
    Класс для подсчета рекомендуемого пульса для различных типов тренировок.
    Все методы являются статическими.
    """

    @staticmethod
    def calculate_max_heart_rate(age):
        """
        Рассчитывает максимальную частоту пульса (ЧСС макс) по формуле: 220 - возраст
        """
        return 220 - age

    @staticmethod
    def calculate_target_zone(age, intensity_min, intensity_max):
        """
        Рассчитывает целевую зону пульса на основе интенсивности в %
        """
        max_hr = HeartRateCalculator.calculate_max_heart_rate(age)
        min_hr = int(max_hr * intensity_min / 100)
        max_hr = int(max_hr * intensity_max / 100)
        return (min_hr, max_hr)

    @staticmethod
    def get_strength_hr(age):
        """Рекомендуемый пульс для силовой тренировки (Strength)"""
        return HeartRateCalculator.calculate_target_zone(age, 70, 85)

    @staticmethod
    def get_power_hr(age):
        """Рекомендуемый пульс для взрывной тренировки (Power)"""
        return HeartRateCalculator.calculate_target_zone(age, 80, 90)

    @staticmethod
    def get_posture_hr(age):
        """Рекомендуемый пульс для оздоровительной тренировки (Posture)"""
        return HeartRateCalculator.calculate_target_zone(age, 60, 75)

    @staticmethod
    def get_endurance_hr(age):
        """Рекомендуемый пульс для тренировки на выносливость (Endurance)"""
        return HeartRateCalculator.calculate_target_zone(age, 75, 85)

    @staticmethod
    def get_core_hr(age):
        """Рекомендуемый пульс для тренировки кора (Core)"""
        return HeartRateCalculator.calculate_target_zone(age, 65, 80)

    @staticmethod
    def get_lower_hr(age):
        """Рекомендуемый пульс для тренировки ног (Lower)"""
        return HeartRateCalculator.calculate_target_zone(age, 70, 85)

    @staticmethod
    def get_superset_hr(age):
        """Рекомендуемый пульс для суперсетов (Superset)"""
        return HeartRateCalculator.calculate_target_zone(age, 75, 88)

    @staticmethod
    def get_full_body_hr(age):
        """Рекомендуемый пульс для тренировки всего тела (Full-Body)"""
        return HeartRateCalculator.calculate_target_zone(age, 70, 85)

    @staticmethod
    def get_street_hr(age):
        """Рекомендуемый пульс для уличной тренировки (Street)"""
        return HeartRateCalculator.calculate_target_zone(age, 75, 90)

    @staticmethod
    def get_hiit_hr(age):
        """Рекомендуемый пульс для ВИИТ тренировки (HIIT)"""
        return HeartRateCalculator.calculate_target_zone(age, 85, 95)

    @staticmethod
    def get_all_workouts_hr(age):
        """
        Возвращает словарь с рекомендуемым пульсом для всех типов тренировок
        """
        workouts = {
            'Strength': HeartRateCalculator.get_strength_hr(age),
            'Power': HeartRateCalculator.get_power_hr(age),
            'Posture': HeartRateCalculator.get_posture_hr(age),
            'Endurance': HeartRateCalculator.get_endurance_hr(age),
            'Core': HeartRateCalculator.get_core_hr(age),
            'Lower': HeartRateCalculator.get_lower_hr(age),
            'Superset': HeartRateCalculator.get_superset_hr(age),
            'Full-Body': HeartRateCalculator.get_full_body_hr(age),
            'Street': HeartRateCalculator.get_street_hr(age),
            'HIIT': HeartRateCalculator.get_hiit_hr(age)
        }
        return workouts


# Пример использования
if __name__ == "__main__":
    age = 25

    # Получить пульс для конкретной тренировки
    strength_hr = HeartRateCalculator.get_strength_hr(age)
    print(f"Strength HR: {strength_hr[0]}-{strength_hr[1]} bpm")

    # Получить пульс для всех тренировок
    all_workouts = HeartRateCalculator.get_all_workouts_hr(age)
    print("\nAll workouts heart rates:")
    for workout, hr_range in all_workouts.items():
        print(f"{workout}: {hr_range[0]}-{hr_range[1]} bpm")

    # Рассчитать максимальный пульс
    max_hr = HeartRateCalculator.calculate_max_heart_rate(age)
    print(f"\nMax HR for age {age}: {max_hr} bpm")