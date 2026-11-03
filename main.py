"""Главная консольная программа PostalService."""
from postal_service import Letter, Bandrol, Parcel, DeliveryCalculator
from postal_service import DeliveryType, PostalRepository
from report_export import export_to_docx


def ask_float(prompt):
    while True:
        try:
            value = float(input(prompt).replace(",", "."))
            if value <= 0:
                raise ValueError
            return value
        except ValueError:
            print("Введите положительное число.")


def create_item():
    print("\nТип отправления: 1 — Письмо, 2 — Бандероль, 3 — Посылка")
    choice = input("Выберите тип: ").strip()
    classes = {"1": Letter, "2": Bandrol, "3": Parcel}
    if choice not in classes:
        print("Неизвестный тип.")
        return None
    cls = classes[choice]
    sender = input("Отправитель: ").strip() or "Не указан"
    recipient = input("Получатель: ").strip() or "Не указан"
    distance = ask_float("Расстояние, км: ")
    weight = ask_float("Вес, кг: ")
    print("Габариты указываются в сантиметрах.")
    length = ask_float("Длина: ")
    width = ask_float("Ширина: ")
    height = ask_float("Высота: ")
    try:
        return cls(sender, recipient, distance, weight, length, width, height)
    except ValueError as error:
        print(f"Ошибка: {error}")
        return None


def main():
    repository = PostalRepository()
    while True:
        print("\n=== POSTALSERVICE ===")
        print("1. Рассчитать стоимость отправления")
        print("2. Показать историю расчётов")
        print("3. Экспортировать историю в DOCX")
        print("0. Выход")
        command = input("Ваш выбор: ").strip()

        if command == "1":
            item = create_item()
            if item is None:
                continue
            print("\nТип доставки: 1 — Стандартная, 2 — Экспресс, 3 — Экономичная")
            delivery_choice = input("Выберите доставку: ").strip()
            delivery_types = {
                "1": DeliveryType.STANDARD,
                "2": DeliveryType.EXPRESS,
                "3": DeliveryType.ECONOMY
            }
            if delivery_choice not in delivery_types:
                print("Неизвестный тип доставки.")
                continue
            result = DeliveryCalculator(item, delivery_types[delivery_choice]).calculate()
            record_id = repository.save(result)
            print("\n--- РЕЗУЛЬТАТ РАСЧЁТА ---")
            print(f"Категория: {result['category']}")
            print(f"Доставка: {result['delivery_type']} ({result['delivery_days']} дн.)")
            print(f"Расчётный вес: {result['chargeable_weight_kg']:.2f} кг")
            print(f"Стоимость: {result['total']:.2f} руб.")
            print(f"Сохранено в SQLite, запись №{record_id}")

        elif command == "2":
            rows = repository.get_all()
            if not rows:
                print("История пуста.")
            for row in rows:
                print(f"#{row['id']} | {row['category']} | "
                      f"{row['sender']} → {row['recipient']} | "
                      f"{row['delivery_type']} | {row['total']:.2f} руб.")

        elif command == "3":
            path = export_to_docx(repository.get_all())
            print(f"Отчёт сохранён: {path}")

        elif command == "0":
            print("Работа завершена.")
            break
        else:
            print("Введите 0, 1, 2 или 3.")


if __name__ == "__main__":
    main()
