"""Тарифный расчёт стоимости доставки."""
from enum import Enum
from .models import PostalItem


class DeliveryType(Enum):
    STANDARD = ("Стандартная", 1.0, 5)
    EXPRESS = ("Экспресс", 1.8, 2)
    ECONOMY = ("Экономичная", 0.8, 9)

    def __init__(self, label, multiplier, days):
        self.label = label
        self.multiplier = multiplier
        self.days = days

    def __str__(self):
        return self.label

    def __repr__(self):
        return f"DeliveryType.{self.name}"


class DeliveryCalculator:
    """Вычисляет тариф по категории, расстоянию, весу, объёму и сроку."""

    DISTANCE_RATE = 0.12       # руб. за км
    WEIGHT_RATE = 35.0         # руб. за расчётный кг
    VOLUME_RATE = 0.002        # руб. за см³
    MIN_PRICE = 80.0

    def __init__(self, item: PostalItem, delivery_type: DeliveryType):
        if not isinstance(item, PostalItem):
            raise TypeError("item должен быть объектом PostalItem.")
        if not isinstance(delivery_type, DeliveryType):
            raise TypeError("Неизвестный тип доставки.")
        self.item = item
        self.delivery_type = delivery_type

    def calculate(self):
        item = self.item
        chargeable_weight = max(item.weight_kg, item.volumetric_weight_kg)
        distance_cost = item.distance_km * self.DISTANCE_RATE
        weight_cost = chargeable_weight * self.WEIGHT_RATE
        volume_cost = item.volume_cm3 * self.VOLUME_RATE
        subtotal = item.base_rate + distance_cost + weight_cost + volume_cost
        total = max(self.MIN_PRICE, subtotal) * self.delivery_type.multiplier
        return {
            "category": item.category,
            "sender": item.sender,
            "recipient": item.recipient,
            "distance_km": item.distance_km,
            "weight_kg": item.weight_kg,
            "volume_cm3": item.volume_cm3,
            "chargeable_weight_kg": chargeable_weight,
            "delivery_type": self.delivery_type.label,
            "delivery_days": self.delivery_type.days,
            "base_rate": item.base_rate,
            "distance_cost": distance_cost,
            "weight_cost": weight_cost,
            "volume_cost": volume_cost,
            "total": round(total, 2)
        }

    def __call__(self):
        return self.calculate()

    def __repr__(self):
        return (f"DeliveryCalculator(item={self.item!r}, "
                f"delivery_type={self.delivery_type!r})")

    def __str__(self):
        return f"Расчёт: {self.item.category}, {self.delivery_type.label}"
