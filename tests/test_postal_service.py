import pytest
from postal_service import (
    Letter, Bandrol, Parcel, DeliveryCalculator, DeliveryType,
    PostalRepository
)


@pytest.fixture
def letter():
    return Letter("Иван", "Пётр", 500, 0.2, 20, 15, 1)


def test_letter_category(letter):
    assert letter.category == "Письмо"


def test_subclass_base_rates():
    assert Letter("a", "b", 10, .1, 10, 10, 1).base_rate == 60
    assert Bandrol("a", "b", 10, .5, 20, 15, 5).base_rate == 90
    assert Parcel("a", "b", 10, 2, 30, 20, 10).base_rate == 140


def test_volume(letter):
    assert letter.volume_cm3 == 300


def test_invalid_weight():
    with pytest.raises(ValueError):
        Letter("a", "b", 10, 0, 10, 10, 1)


def test_invalid_distance():
    with pytest.raises(ValueError):
        Letter("a", "b", -1, .2, 10, 10, 1)


def test_standard_calculation(letter):
    result = DeliveryCalculator(letter, DeliveryType.STANDARD).calculate()
    assert result["total"] > 0
    assert result["delivery_days"] == 5


def test_express_is_more_expensive(letter):
    standard = DeliveryCalculator(letter, DeliveryType.STANDARD).calculate()
    express = DeliveryCalculator(letter, DeliveryType.EXPRESS).calculate()
    assert express["total"] > standard["total"]


def test_database_save_and_read(tmp_path, letter):
    repository = PostalRepository(tmp_path / "test.db")
    result = DeliveryCalculator(letter, DeliveryType.STANDARD).calculate()
    record_id = repository.save(result)
    rows = repository.get_all()
    assert record_id == 1
    assert len(rows) == 1
    assert rows[0]["category"] == "Письмо"
