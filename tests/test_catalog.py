from datetime import date

import pytest

from tram_catalog.catalog import TramCatalog
from tram_catalog.errors import DuplicateIDError, InvalidRouteError, NotFoundError
from tram_catalog.models import TramRoute


def test_add() -> None:
    """Тест добавление маршрута в каталог"""

    # создаем пустой каталог
    catalog = TramCatalog()
    # создаем маршрут
    data = date(2026, 10, 30)
    route = TramRoute('route-000', '15А', 'городской', data, True, "дневной")
    # добавляем маршрут
    catalog.add(route)

    assert len(catalog) == 1
    assert catalog.get('route-000') == route

def test_add_duplicate_id() -> None:
    """Тест добавление маршрута с дубликатом идентификатора"""

    # создаем пустой каталог
    catalog = TramCatalog()

    # создаем первый маршрут
    data = date(2026, 10, 30)
    route1 = TramRoute('route-000', '15А', 'городской', data, True, "дневной")
    # создаем второй маршрут
    route2 = TramRoute('route-000', '6Б', 'городской', data, False, "дневной")
    
    # добавляем первый маршрут
    catalog.add(route1)
    # добавляем второй маршрут
    with pytest.raises(DuplicateIDError):
        catalog.add(route2)

    assert len(catalog) == 1
    assert catalog.get('route-000') == route1

def test_add_invalid_object() -> None:
    """Проверка добавление постороннего объекта"""

    # создаем пустой каталог
    catalog = TramCatalog()

    # создаем маршрут
    route = 'Маршрут 1'
    
    # добавляем маршрут
    with pytest.raises(InvalidRouteError):
        catalog.add(route)               # type: ignore[arg-type]

def test_get() -> None:
    """Тест получение маршрута по идентификатору"""
    
    catalog = TramCatalog()

    data = date(2026, 10, 30)
    route1 = TramRoute('route-000', '15А', 'городской', data, True, "дневной")

    route2 = TramRoute('route-001', '6Б', 'городской', data, False, "дневной")

    route3 = TramRoute('route-002', '13', 'городской', data, False, "ночной")
    
    catalog.add(route1)
    catalog.add(route2)
    catalog.add(route3)

    route = catalog.get('route-001')
    assert route == route2

def test_get_missing_id() -> None:
    """Тест получение маршрута по несуществующем ид - ошибка"""

    catalog = TramCatalog()

    data = date(2026, 10, 30)
    route = TramRoute('route-000', '6Б', 'городской', data, False, "дневной")
    catalog.add(route)

    with pytest.raises(NotFoundError):
        catalog.get('route-001')

def test_remove() -> None:
    """Тест удаление маршрута по идентификатору"""
    
    catalog = TramCatalog()

    data = date(2026, 10, 30)
    route1 = TramRoute('route-000', '15А', 'городской', data, True, "дневной")

    route2 = TramRoute('route-001', '6Б', 'городской', data, False, "дневной")

    route3 = TramRoute('route-002', '13', 'городской', data, False, "ночной")
    
    catalog.add(route1)
    catalog.add(route2)
    catalog.add(route3)

    catalog.remove('route-001')
    assert len(catalog) == 2
    assert catalog.get('route-000') == route1
    assert catalog.get('route-002') == route3

def test_remove_missing_id() -> None:
    """Тест удаление маршрута по несуществующем ид - ошибка"""

    catalog = TramCatalog()

    data = date(2026, 10, 30)
    route = TramRoute('route-000', '6Б', 'городской', data, False, "дневной")
    catalog.add(route)

    with pytest.raises(NotFoundError):
        catalog.remove('route-001')

def test_len() -> None:
    """Тест длины каталога"""

    catalog = TramCatalog()

    assert len(catalog) == 0

    data = date(2026, 10, 30)
    route1 = TramRoute('route-000', '6Б', 'городской', data, False, "дневной")

    route2 = TramRoute('route-001', '15А', 'городской', data, True, "дневной")

    catalog.add(route1)
    catalog.add(route2)

    assert len(catalog) == 2

    catalog.remove('route-001')

    assert len(catalog) == 1

def test_contains() -> None:
    """Проверка наличия/отстутствия ид в каталоге"""

    catalog = TramCatalog()
    
    data = date(2026, 10, 30)
    route = TramRoute('route-000', '6Б', 'городской', data, False, "дневной")
    catalog.add(route)

    assert 'route-000' in catalog
    assert 'route-001' not in catalog

def test_iter() -> None:
    """Тест перебор маршрутов в порядке добавления"""
    
    catalog = TramCatalog()

    data = date(2026, 10, 30)
    route1 = TramRoute('route-000', '15А', 'городской', data, True, "дневной")

    route2 = TramRoute('route-001', '6Б', 'городской', data, False, "дневной")

    route3 = TramRoute('route-002', '13', 'городской', data, False, "ночной")
    
    catalog.add(route2)
    catalog.add(route1)
    catalog.add(route3)

    res = [route2, route1, route3]

    assert list(catalog) == res
    assert list(catalog) == res
  
def test_find_by_category() -> None:
    """Тест получение маршрутов по категории"""
    
    catalog = TramCatalog()

    empty_catalog = TramCatalog()

    data = date(2026, 10, 30)
    route1 = TramRoute('route-000', '15А', 'пригородный', data, True, "дневной")

    route2 = TramRoute('route-001', '6Б', 'городской', data, False, "дневной")

    route3 = TramRoute('route-002', '13', 'пригородный', data, False, "ночной")
    
    catalog.add(route1)
    catalog.add(route2)
    catalog.add(route3)

    res1: list[TramRoute] = [route2]
    res2: list[TramRoute] = [route1, route3]

    assert catalog.find_by_category('городской') == res1
    assert catalog.find_by_category('пригородный') == res2
    assert empty_catalog.find_by_category('городской') == []

def test_find_by_name() -> None:
    """Тест поиска всех маршрутов с одинаковым названием"""

    catalog = TramCatalog()

    data = date(2026, 10, 30)
    route1 = TramRoute('route-000', '15А', 'городской', data, True, "дневной")
    route2 = TramRoute('route-001', '6Б', 'городской', data, False, "дневной")
    route3 = TramRoute('route-002', '15А', 'пригородный', data, False, "ночной")

    catalog.add(route1)
    catalog.add(route2)
    catalog.add(route3)

    res1: list[TramRoute] = [route1, route3]
    res2: list[TramRoute] = [route2]

    assert catalog.find_by_name('15А') == res1
    assert catalog.find_by_name('6Б') == res2

def test_find_by_name_ignores_case() -> None:
    """Тест поиска названия без учета регистра"""

    catalog = TramCatalog()

    data = date(2026, 10, 30)
    route1 = TramRoute('route-000', '15Абё', 'городской', data, True, "дневной")
    route2 = TramRoute('route-001', '6Б', 'городской', data, False, "дневной")

    catalog.add(route1)
    catalog.add(route2)

    res: list[TramRoute] = [route1]

    assert catalog.find_by_name('15аБЁ') == res

def test_find_by_name_no_matches() -> None:
    """Тест поиска названия без совпадений."""

    catalog = TramCatalog()
    empty_catalog = TramCatalog()

    data = date(2026, 10, 30)
    route = TramRoute('route-000', '15А', 'городской', data, True, "дневной")

    catalog.add(route)

    res: list[TramRoute] = []

    assert catalog.find_by_name('41Б') == res
    assert empty_catalog.find_by_name('15А') == res
