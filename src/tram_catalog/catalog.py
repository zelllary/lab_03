from collections.abc import Iterator

from .errors import DuplicateIDError, InvalidRouteError, NotFoundError
from .models import TramRoute


class TramCatalog:
    """Каталог маршрутов"""

    def __init__(self) -> None:
        """Инициализация класса"""

        self._items: dict[str, TramRoute] = {}
        self._category_index: dict[str, dict[str, TramRoute]] = {}

    def add(self, item: TramRoute) -> None:
        """Добавление маршрута в каталог"""

        # проверяем тип добавляемого маршрута
        if (not isinstance(item, TramRoute)):
            raise InvalidRouteError('Посторонний объект')

        # проверяем, чтобы идентификатор не дублировался
        if (item.route_id in self._items):
            raise DuplicateIDError('Такой идентификатор уже существует')

        # если маршрутов с категорией еще не было
        if item.category not in self._category_index:
            self._category_index[item.category] = {}

        # добавляем маршрут по идентификатору
        self._items[item.route_id] = item

        # записываем маршрут во внутренний словарь
        self._category_index[item.category][item.route_id] = item

    def get(self, item_id: str) -> TramRoute:
        """Получение маршрута по идентификатору"""

        # проверяем наличие маршрута с таким идентификатором в каталоге
        if (item_id not in self._items):
            raise NotFoundError('Маршрута с таким идентификатором нет в каталоге')

        return self._items[item_id]

    def remove(self, item_id: str) -> None:
        """Удаление маршрута по идентификатору"""

        # проверяем наличие маршрута с таким идентификатором в каталоге
        if (item_id not in self._items):
            raise NotFoundError('Маршрута с таким идентификатором нет в каталоге')
        
        # сохраняем маршрут
        item = self._items[item_id]

        # удаляем из словаря по категориям
        del self._category_index[item.category][item_id]

        # если категория больше не содержит маршрутов
        if not self._category_index[item.category]:
            del self._category_index[item.category]

        # удаляем
        del self._items[item_id]

    def find_by_category(self, category: str) -> list[TramRoute]:
        """Поиск маршрутов по категории с использованием индекса"""

        # создаем список для маршрутов
        res: list[TramRoute] = []

        # если категория пустая
        if category not in self._category_index:
            return res

        # если категория не пустая - берем значения словаря и преобразуем в список
        res = list(self._category_index[category].values())

        return res 

    def find_by_name(self, query: str) -> list[TramRoute]:
        """Поиск маршрутов по части названия без учёта регистра"""

        # создаем список для маршрутов
        res: list[TramRoute] = []

        # приводим название маршрута к нижнему регистру
        lower_query = query.casefold()

        # перебираем маршруты
        for route in self._items.values():
            # если название совпадает - добавлем в список
            if lower_query in route.name.casefold():
                res.append(route)

        return res

    def __len__(self) -> int:
        """Количество маршрутов"""

        return len(self._items)

    def __iter__(self) -> Iterator[TramRoute]:
        """Перебор маршрутов в порядке добавления"""

        yield from self._items.values()

    def __contains__(self, item_id: str) -> bool:
        """Проверка наличия идентификатора в каталоге"""

        return item_id in self._items

    def read_only_view(self) -> tuple[TramRoute, ...]:
        """Возвращает неизменяемый кортеж маршрутов в порядке добавления"""

        # создаем кортеж с маршрутами
        res = tuple(self._items.values())
        return res