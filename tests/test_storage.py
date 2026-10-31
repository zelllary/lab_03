import json
from datetime import date
from pathlib import Path

import pytest

from tram_catalog.catalog import TramCatalog
from tram_catalog.errors import DamagedFileError, UnsupportedFormatError
from tram_catalog.models import TramRoute
from tram_catalog.storage import load_catalog, save_catalog


def test_save_load_catalog(tmp_path: Path) -> None:
    """Тест сохранения и загрузки всех полей маршрутов"""

    # создаем каталог
    catalog = TramCatalog()

    # создаем маршруты с разными значениями полей
    route1 = TramRoute(
        'route-000',
        '15А',
        'городской',
        date(2026, 10, 29),
        True,
        'дневной',
    )
    route2 = TramRoute(
        'route-001',
        '6Б',
        'пригородный',
        date(2026, 10, 30),
        False,
        'ночной',
    )

    catalog.add(route1)
    catalog.add(route2)

    # путь к файлу во временной папке
    file = tmp_path / 'catalog.json'

    # сохраняем и загружаем каталог
    save_catalog(catalog, file)
    loaded_catalog = load_catalog(file)

    # сравниваем маршруты и порядок их расположения
    assert list(loaded_catalog) == list(catalog)

def test_save_load_empty_catalog(tmp_path: Path) -> None:
    """Тест сохранения и загрузки пустого каталога"""

    catalog = TramCatalog()
    file = tmp_path / 'catalog.json'

    save_catalog(catalog, file)
    loaded_catalog = load_catalog(file)

    assert len(loaded_catalog) == 0
    assert list(loaded_catalog) == []


def test_saved_format_version(tmp_path: Path) -> None:
    """Тест записи версии формата в корень документа"""

    catalog = TramCatalog()
    file = tmp_path / 'catalog.json'

    save_catalog(catalog, file)

    # читаем данные из файла
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert type(data['format_version']) is int
    assert data['format_version'] == 1
    assert data['items'] == []


def test_load_invalid_json(tmp_path: Path) -> None:
    """Тест загрузки синтаксически поврежденного JSON"""

    file = tmp_path / 'catalog.json'

    with open(file, 'w', encoding='utf-8') as f:
        # записываем неверный json
        f.write('{"format_version": 1, "items": [')

    with pytest.raises(DamagedFileError):
        load_catalog(file)


def test_load_unsupported_version(tmp_path: Path) -> None:
    """Тест загрузки неподдерживаемой версии формата"""

    file = tmp_path / 'catalog.json'
    data: dict[str, object] = {
        'format_version': 2,
        'items': [],
    }

    with open(file, 'w', encoding='utf-8') as f:
        # json.dump преобразует данные в JSON и записывает в открытый файл
        json.dump(data, f, ensure_ascii=False)

    with pytest.raises(UnsupportedFormatError):
        load_catalog(file)


def test_load_list(tmp_path: Path) -> None:
    """Тест загрузки списка вместо корневого словаря"""

    file = tmp_path / 'catalog.json'

    with open(file, 'w', encoding='utf-8') as f:
        json.dump([], f)

    with pytest.raises(DamagedFileError):
        load_catalog(file)


def test_load_invalid_items(tmp_path: Path) -> None:
    """Тест отсутствующего списка маршрутов и неверного его типа"""

    file = tmp_path / 'catalog.json'
    documents: list[dict[str, object]] = [
        {'format_version': 1},
        {'format_version': 1, 'items': {}},
        {'format_version': 1, 'items': None},
    ]

    # каждый вариант записываем и проверяем отдельно
    for data in documents:
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f)

        with pytest.raises(DamagedFileError):
            load_catalog(file)


def test_load_missing_route_field(tmp_path: Path) -> None:
    """Тест отсутствующего названия в записи маршрута"""

    file = tmp_path / 'catalog.json'
    route = {
        'route_id': 'route-000',
        'category': 'городской',
        'open_date': '2026-10-30',
        'active': True,
        'operating_mode': 'дневной',
    }
    data: dict[str, object] = {
        'format_version': 1,
        'items': [route],
    }

    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

    with pytest.raises(DamagedFileError):
        load_catalog(file)


def test_load_invalid_date(tmp_path: Path) -> None:
    """Тест несуществующей даты в записи маршрута"""

    file = tmp_path / 'catalog.json'
    route = {
        'route_id': 'route-000',
        'name': '15А',
        'category': 'городской',
        'open_date': '2026-02-30',
        'active': True,
        'operating_mode': 'дневной',
    }

    data: dict[str, object] = {
        'format_version': 1,
        'items': [route],
    }

    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

    with pytest.raises(DamagedFileError):
        load_catalog(file)


def test_load_invalid_name(tmp_path: Path) -> None:
    """Тест некорректного названия при загрузке"""

    file = tmp_path / 'catalog.json'
    route = {
        'route_id': 'route-000',
        'name': '015',
        'category': 'городской',
        'open_date': '2026-10-30',
        'active': True,
        'operating_mode': 'дневной',
    }
    data: dict[str, object] = {
        'format_version': 1,
        'items': [route],
    }

    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

    with pytest.raises(DamagedFileError):
        load_catalog(file)


def test_load_duplicate_id(tmp_path: Path) -> None:
    """Тест повторяющихся идентификаторов в файле"""

    file = tmp_path / 'catalog.json'
    route1 = {
        'route_id': 'route-000',
        'name': '15А',
        'category': 'городской',
        'open_date': '2026-10-30',
        'active': True,
        'operating_mode': 'дневной',
    }

    # создаем отдельный словарь, изменение route2 не меняет route1
    route2 = route1.copy()
    route2['name'] = '6Б'

    data: dict[str, object] = {
        'format_version': 1,
        'items': [route1, route2],
    }

    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

    with pytest.raises(DamagedFileError):
        load_catalog(file)


def test_failed_load_preserves_catalog(tmp_path: Path) -> None:
    """Тест сохранения исходного каталога после ошибки загрузки"""

    catalog = TramCatalog()
    route = TramRoute(
        'route-000',
        '6Б',
        'городской',
        date(2026, 10, 30),
        False,
        'ночной',
    )
    catalog.add(route)

    file = tmp_path / 'catalog.json'
    route1 = {
        'route_id': 'route-001',
        'name': '15А',
        'category': 'пригородный',
        'open_date': '2026-10-29',
        'active': True,
        'operating_mode': 'дневной',
    }

    route2 = route1.copy()
    route2['route_id'] = 'route-002'
    route2['name'] = '015'

    data: dict[str, object] = {
        'format_version': 1,
        'items': [route1, route2],
    }

    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

    with pytest.raises(DamagedFileError):
        # присваивание произойдет только после успешного завершения загрузки
        catalog = load_catalog(file)

    assert len(catalog) == 1
    assert list(catalog) == [route]
    assert catalog.get('route-000') == route
    assert 'route-001' not in catalog
    assert 'route-002' not in catalog


def test_invalid_version_type(tmp_path: Path) -> None:
    """Тест отсутствующей версии и неверного ее типа"""

    file = tmp_path / 'catalog.json'
    documents: list[dict[str, object]] = [
        {'items': []},
        {'format_version': True, 'items': []},
        {'format_version': '1', 'items': []},
        {'format_version': 1.0, 'items': []},
    ]

    for data in documents:
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f)

        with pytest.raises(DamagedFileError):
            load_catalog(file)


def test_load_route_not_dict(tmp_path: Path) -> None:
    """Тест записи маршрута, которая не является словарем"""

    file = tmp_path / 'catalog.json'
    data: dict[str, object] = {
        'format_version': 1,
        'items': ['15А'],
    }

    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

    with pytest.raises(DamagedFileError):
        load_catalog(file)

