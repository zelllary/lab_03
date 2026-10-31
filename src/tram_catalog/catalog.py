from collections.abc import Iterator

from tram_catalog.errors import DuplicateIDError, InvalidRouteError, NotFoundError

from .models import TramRoute


class TramCatalog:
    """Каталог маршрутов"""

    def __init__(self) -> None:
        """Инициализация класса"""

        self._items: dict[str, TramRoute] = {}

    def add(self, item: TramRoute) -> None:
        """Добавление маршрута в каталог"""

        # проверяем тип добавляемого маршрута
        if (not isinstance(item, TramRoute)):
            raise InvalidRouteError('Посторонний объект')

        # проверяем, чтобы идентификатор не дублировался
        if (item.route_id in self._items):
            raise DuplicateIDError('Такой идентификатор уже существует')

        # добавляем маршрут по идентификатору
        self._items[item.route_id] = item

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

        # удаляем
        del self._items[item_id]

    def find_by_category(self, category: str) -> list[TramRoute]:
        """Поиск все маршрутов заданной категории"""

        # создаем список для маршрутов
        res: list[TramRoute] = []

        # перебираем маршруты и проверяем их категорию
        for route in self._items.values():
            # если нужная категория - добавляем в список
            if route.category == category:
                res.append(route)

        return res 

    def find_by_name(self, query: str) -> list[TramRoute]:
        """Поиск маршрутов по имени"""

        # создаем список для маршрутов
        res: list[TramRoute] = []

        # приводим название маршрута к нижнему регистру
        lower_query = query.casefold()

        # перебираем маршруты
        for route in self._items.values():
            # если название совпадает - добавлем в список
            if route.name.casefold() == lower_query:
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