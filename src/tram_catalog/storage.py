import json
from datetime import date
from pathlib import Path

from .catalog import TramCatalog
from .constants import FORMAT_VERSION
from .errors import (
    DamagedFileError,
    DuplicateIDError,
    InvalidRouteError,
    UnsupportedFormatError,
)
from .models import TramRoute


def route_to_dict(route: TramRoute) -> dict[str, str | bool]:
    """Преобразование маршрута в словарь"""

    # создаем пустой словарь
    route_dict: dict[str, str | bool] = {}
    # заполняем его
    route_dict['route_id'] = route.route_id
    route_dict['name'] = route.name
    route_dict['category'] = route.category
    route_dict['open_date'] = route.open_date.isoformat()
    route_dict['active'] = route.active
    route_dict['operating_mode'] = route.operating_mode

    return route_dict

def save_catalog(catalog: TramCatalog, file: str | Path) -> None:
    """Запись каталога в файл json"""

    route_dicts: list[dict[str, str | bool]] = []

    # заполняем список маршрутами в формате словарей
    for route in catalog:
        route_dicts.append(route_to_dict(route))

    # результирующий словарь для записи
    res_dict = {
        "format_version": FORMAT_VERSION,
        "items": route_dicts
    }

    # открываем файл и записываем в него
    with open(file, "w", encoding="utf-8") as f:
        json.dump(res_dict, f, ensure_ascii=False, indent=4)

def route_from_dict(data: object) -> TramRoute:
    """Преобразование из данных (словарей) в маршрут"""

    # если данные не словарь
    if (not isinstance(data, dict)):
        raise DamagedFileError('Неверный формат данных в файле')

    # пытаемся создать маршрут из данных
    try:
        route = TramRoute(
            data['route_id'],
            data['name'],
            data['category'],
            date.fromisoformat(data['open_date']),
            data['active'],
            data['operating_mode']
        )

        return route
    
    except (KeyError, TypeError, ValueError, InvalidRouteError):
        raise DamagedFileError('Неверный формат данных в файле')

def load_catalog(file: str | Path) -> TramCatalog:
    """Создание каталога из данных из файла"""

    try:
        # открываем файл для чтения
        with open(file, "r", encoding="utf-8") as f:
            read_f = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise DamagedFileError('Не удалось считать данные из файла')
    # если данные не словарь
    if (not isinstance(read_f, dict)):
        raise DamagedFileError('Данные в файле не словарь')
    # если версия формата не число
    if type(read_f.get("format_version")) != int:
        raise DamagedFileError('Неизвестный тип версии формата')
    # неподдерживаемая версия
    if read_f.get('format_version') != FORMAT_VERSION:
        raise UnsupportedFormatError('Неподдерживаемая версия')
    # маршруты в файле должны быть списком
    if (not isinstance(read_f.get('items'), list)):
        raise DamagedFileError('Неподдерживаемый формат данных в файле') 

    catalog = TramCatalog()

    # перебираем маршруты из файла
    for item in read_f['items']:
        # преобразуем в маршрут 
        route = route_from_dict(item)
        # добавляем в каталог
        try:
            catalog.add(route)
        except DuplicateIDError:
            raise DamagedFileError('Повторяющийся идентификатор в файле')

    return catalog