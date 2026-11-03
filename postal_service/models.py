"""Модели почтовых отправлений с валидацией managed-атрибутов."""
from abc import ABC, abstractmethod


class PostalItem(ABC):
    """Абстрактное почтовое отправление."""

    def __init__(self, sender: str, recipient: str, distance_km: float,
                 weight_kg: float, length_cm: float, width_cm: float,
                 height_cm: float):
        self.sender = sender
        self.recipient = recipient
        self.distance_km = distance_km
        self.weight_kg = weight_kg
        self.length_cm = length_cm
        self.width_cm = width_cm
        self.height_cm = height_cm

    @property
    def distance_km(self):
        return self._distance_km

    @distance_km.setter
    def distance_km(self, value):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("Расстояние должно быть положительным числом.")
        self._distance_km = float(value)

    @property
    def weight_kg(self):
        return self._weight_kg

    @weight_kg.setter
    def weight_kg(self, value):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("Вес должен быть положительным числом.")
        self._weight_kg = float(value)

    @property
    def length_cm(self):
        return self._length_cm

    @length_cm.setter
    def length_cm(self, value):
        self._length_cm = self._validate_dimension(value)

    @property
    def width_cm(self):
        return self._width_cm

    @width_cm.setter
    def width_cm(self, value):
        self._width_cm = self._validate_dimension(value)

    @property
    def height_cm(self):
        return self._height_cm

    @height_cm.setter
    def height_cm(self, value):
        self._height_cm = self._validate_dimension(value)

    @staticmethod
    def _validate_dimension(value):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("Габариты должны быть положительными числами.")
        return float(value)

    @property
    def volume_cm3(self):
        return self.length_cm * self.width_cm * self.height_cm

    @property
    def volumetric_weight_kg(self):
        # Условный коэффициент объёмного веса: 5000 см³ = 1 кг.
        return self.volume_cm3 / 5000

    @property
    @abstractmethod
    def category(self):
        """Название категории отправления."""

    @property
    @abstractmethod
    def base_rate(self):
        """Базовый тариф категории."""

    def common_data(self):
        return {
            "sender": self.sender, "recipient": self.recipient,
            "distance_km": self.distance_km, "weight_kg": self.weight_kg,
            "length_cm": self.length_cm, "width_cm": self.width_cm,
            "height_cm": self.height_cm, "volume_cm3": self.volume_cm3
        }

    def __str__(self):
        return f"{self.category}: {self.sender} → {self.recipient}"

    def __repr__(self):
        return (f"{self.__class__.__name__}(sender={self.sender!r}, "
                f"recipient={self.recipient!r}, weight_kg={self.weight_kg})")


class Letter(PostalItem):
    """Письмо. Небольшой вес и компактные габариты."""

    @property
    def category(self):
        return "Письмо"

    @property
    def base_rate(self):
        return 60.0

    def __str__(self):
        return f"Письмо от {self.sender} для {self.recipient}"

    def __repr__(self):
        return f"Letter({self.sender!r}, {self.recipient!r}, {self.weight_kg})"


class Bandrol(PostalItem):
    """Бандероль для печатной продукции и небольших вложений."""

    @property
    def category(self):
        return "Бандероль"

    @property
    def base_rate(self):
        return 90.0

    def __str__(self):
        return f"Бандероль: {self.sender} → {self.recipient}"

    def __repr__(self):
        return f"Bandrol({self.sender!r}, {self.recipient!r}, {self.weight_kg})"


class Parcel(PostalItem):
    """Посылка для предметов и товаров."""

    @property
    def category(self):
        return "Посылка"

    @property
    def base_rate(self):
        return 140.0

    def __str__(self):
        return f"Посылка: {self.sender} → {self.recipient}"

    def __repr__(self):
        return f"Parcel({self.sender!r}, {self.recipient!r}, {self.weight_kg})"

