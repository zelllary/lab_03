from datetime import date, timedelta

import pytest

from tram_catalog.errors import InvalidRouteError
from tram_catalog.models import TramRoute


def test_create_valid_route() -> None:
    """Тест на создание корректного маршрута"""

    data = date(2026, 10, 29)
    route = TramRoute('route-000', '15Абё', 'городской', data, True, "дневной")

    assert route.route_id == 'route-000'
    assert route.name == '15Абё'
    assert route.category == 'городской'
    assert route.open_date == date(2026, 10, 29)
    assert route.active == True
    assert route.operating_mode == 'дневной'

def test_name_is_zero() -> None:
    """Тест на название состоящее только из 0"""

    with pytest.raises(InvalidRouteError):
        data = date(2026, 10, 29)
        TramRoute('route-000', '0', 'городской', data, True, "дневной")

def test_empty_name() -> None:
    """Тест на пустую строку в названии маршрута"""

    with pytest.raises(InvalidRouteError):
        data = date(2026, 10, 29)
        TramRoute('route-000', '', 'городской', data, True, "дневной")

def test_leading_zero_in_name() -> None:
    """Тест на ведущий ноль в названии маршрута"""

    with pytest.raises(InvalidRouteError):
        data = date(2026, 10, 29)
        TramRoute('route-000', '015', 'городской', data, True, "дневной")

def test_letter_in_name() -> None:
    """Тест на букву в названии маршрута"""

    with pytest.raises(InvalidRouteError):
        data = date(2026, 10, 29)
        TramRoute('route-000', '15A', 'городской', data, True, "дневной")

def test_invalid_prefix_id() -> None:
    """Тест на некорректный префикс идентификатора"""

    with pytest.raises(InvalidRouteError):
        data = date(2026, 10, 29)
        TramRoute('rout-000', '15', 'городской', data, True, "дневной")

def test_invalid_number_id() -> None:
    """Тест на некорректное число в идентификаторе (меньше цифр чем нужно)"""

    with pytest.raises(InvalidRouteError):
        data = date(2026, 10, 29)
        TramRoute('route-01', '15', 'городской', data, True, "дневной")

def test_invalid_category() -> None:
    """Тест на некорректную категорию"""

    with pytest.raises(InvalidRouteError):
        data = date(2026, 10, 29)
        TramRoute('route-000', '15', 'межгородской', data, True, "дневной")

def test_invalid_operating_mode() -> None:
    """Тест на некорректный режим работы"""

    with pytest.raises(InvalidRouteError):
        data = date(2026, 10, 29)
        TramRoute('route-000', '15', 'городской', data, True, "утренний")

def test_invalid_active() -> None:
    """Тест на некорректную активность маршрута"""

    with pytest.raises(InvalidRouteError):
        data = date(2026, 10, 29)
        TramRoute('route-000', '15', 'городской', data, 1, "дневной") # type: ignore[arg-type]

def test_invalid_date() -> None:
    """Тест на некорректную дату открытия маршрута"""

    with pytest.raises(InvalidRouteError):
        data = date.today() + timedelta(days=1)
        TramRoute('route-000', '15', 'городской', data, True, "дневной")

def test_latin_letter_in_name() -> None:
    """Тест на латинскую букву в названии маршрута"""

    with pytest.raises(InvalidRouteError):
        data = date(2026, 10, 30)
        TramRoute('route-000', '15Z', 'городской', data, True, "дневной")

def test_max_letter_in_name() -> None:
    """Тест на превышение количества в названии маршрута"""

    with pytest.raises(InvalidRouteError):
        data = date(2026, 10, 30)
        TramRoute('route-000', '15АбЁк', 'городской', data, True, "дневной")




