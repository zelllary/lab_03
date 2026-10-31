from dataclasses import dataclass
from datetime import date

from .constants import (
    MAX_ROUTE_NAME_SUFFIX_LENGTH,
    OPERATING_MODES,
    ROUTE_CATEGORIES,
    RUSSIAN_LETTERS,
)
from .errors import InvalidRouteError


@dataclass(frozen=True)
class TramRoute:
    """Трамвайный маршрут"""
    route_id: str           # идентификатор
    name: str               # название
    category: str           # категория
    open_date: date         # дата открытия
    active: bool            # активность
    operating_mode: str     # режим работы

    def __post_init__(self) -> None:
        """Проверка корректности полей"""

        # проверяем корректность названия
        name = self.name
        if (not isinstance(name, str) or   # если это не строка
            not name.replace(' ', '') or   # или она пустая/состоит из пробелов
            name[0] not in '123456789'):    # первый символ недопустимый
            raise InvalidRouteError('Некорректное название поля')

        # для проверки количества букв
        letter_count: int = 0

        # идем по символам в имени
        for i in range(1, len(name)):
            # если символ цифра 
            if name[i] in '0123456789': 
                # но счетчик букв > 0
                if letter_count != 0:
                    raise InvalidRouteError('Некорректное название поля')
            # если символ - буква
            elif name[i].casefold() in RUSSIAN_LETTERS:
                letter_count += 1
                # если превышено количество букв
                if letter_count > MAX_ROUTE_NAME_SUFFIX_LENGTH:
                    raise InvalidRouteError('Превышено допустимое количество букв в названии')
            # недопустимый символ
            else:
                raise InvalidRouteError('Недопустимый символ')
            

        # проверяем корректность активности
        if (not isinstance(self.active, bool)):
            raise InvalidRouteError('Некорректный тип активности')

        # проверяем корректность даты открытия
        if (not (type(self.open_date) == date)):
            raise InvalidRouteError('Некорректный тип даты открытия')

        if (self.open_date > date.today()): # если дата в будущем
            raise InvalidRouteError('Дата открытия не может быть в будущем')

        # проверяем корректность категории
        if (self.category not in ROUTE_CATEGORIES):
            raise InvalidRouteError('Некорректная категория')
        
        # проверяем корректность режима работы
        if (self.operating_mode not in OPERATING_MODES):
            raise InvalidRouteError('Некорректный режим работы')

        # проверяем корректность идентификатора
        if (not isinstance(self.route_id, str) or # не строка
            self.route_id[:6] != "route-"):       # нет префикса
            raise InvalidRouteError('Некорректный идентификатор: нет префикса "route-"')

        number = self.route_id[6:]

        if (len(number) < 3): # если длина числовой части < 3
            raise InvalidRouteError('Некорректный идентификатор: минимум 3 цифры в числовой части')

        for num in number:
            if num not in "0123456789":
                raise InvalidRouteError('Некорректный идентификатор: некорректные символы в числовой части')
        