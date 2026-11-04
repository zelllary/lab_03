from datetime import date

import pytest

from tram_catalog.catalog import TramCatalog
from tram_catalog.errors import DuplicateIDError
from tram_catalog.models import TramRoute


def test_read_only_view() -> None:
    """Тест независимости кортежа маршрутов от изменений каталога"""

    catalog = TramCatalog()

    data = date(2026, 11, 3)
    route1 = TramRoute('route-000', '15А', 'городской', data, True, 'дневной')
    route2 = TramRoute('route-001', '6Б', 'городской', data, False, 'ночной')
    route3 = TramRoute('route-002', '13', 'пригородный', data, True, 'дневной')

    catalog.add(route2)
    catalog.add(route1)

    res = catalog.read_only_view()

    assert res == (route2, route1)

    catalog.remove('route-001')
    catalog.add(route3)

    assert res == (route2, route1)
    assert list(catalog) == [route1, route3]

def test_index_after_remove() -> None:
    """Тест сохранения остальных маршрутов в индексе после удаления"""

    catalog = TramCatalog()

    data = date(2026, 11, 3)
    route1 = TramRoute('route-000', '15А', 'городской', data, True, 'дневной')
    route2 = TramRoute('route-001', '6Б', 'городской', data, False, 'ночной')
    route3 = TramRoute('route-002', '13', 'пригородный', data, True, 'дневной')

    catalog.add(route1)
    catalog.add(route2)
    catalog.add(route3)

    catalog.remove('route-000')

    assert catalog.find_by_category('городской') == [route2]
    assert catalog.find_by_category('пригородный') == [route3]
    assert 'route-000' not in catalog
    assert len(catalog) == 2


def test_index_after_remove_last() -> None:
    """Тест удаления последнего маршрута категории и повторного добавления"""

    catalog = TramCatalog()

    data = date(2026, 11, 3)
    route1 = TramRoute('route-000', '15А', 'городской', data, True, 'дневной')
    route2 = TramRoute('route-000', '6Б', 'городской', data, False, 'ночной')

    catalog.add(route1)
    catalog.remove('route-000')

    assert catalog.find_by_category('городской') == []
    assert len(catalog) == 0

    catalog.add(route2)

    assert catalog.find_by_category('городской') == [route2]
    assert catalog.get('route-000') == route2
    assert len(catalog) == 1


def test_index_after_duplicate_id() -> None:
    """Тест сохранения индекса при попытке добавить повторяющийся идентификатор"""

    catalog = TramCatalog()

    data = date(2026, 11, 3)
    route1 = TramRoute('route-000', '15А', 'городской', data, True, 'дневной')
    route2 = TramRoute('route-000', '6Б', 'пригородный', data, False, 'ночной')

    catalog.add(route1)

    # проверяем, что добавление вызывает ожидаемую ошибку
    with pytest.raises(DuplicateIDError):
        catalog.add(route2)

    assert catalog.find_by_category('городской') == [route1]
    assert catalog.find_by_category('пригородный') == []
    assert catalog.get('route-000') == route1
    assert len(catalog) == 1


def test_category_search_result_independence() -> None:
    """Тест независимости результата поиска от внутреннего индекса"""

    catalog = TramCatalog()

    data = date(2026, 11, 3)
    route1 = TramRoute('route-000', '15А', 'городской', data, True, 'дневной')
    route2 = TramRoute('route-001', '6Б', 'городской', data, False, 'ночной')

    catalog.add(route1)
    catalog.add(route2)

    res = catalog.find_by_category('городской')

    assert res == [route1, route2]

    # очищаем полученный список
    res.clear()

    assert res == []
    assert catalog.find_by_category('городской') == [route1, route2]
    assert list(catalog) == [route1, route2]
