from datetime import date

from .catalog import TramCatalog
from .models import TramRoute
from .storage import load_catalog, save_catalog


def main() -> None:
    """Демонстрация работы каталога трамвайных маршрутов"""

    # создаем пустой каталог
    catalog = TramCatalog()

    # заполняем его
    data = date(2026, 11, 4)
    route1 = TramRoute('route-000', '15А', 'городской', data, True, 'дневной')
    route2 = TramRoute('route-001', '6Б', 'городской', data, False, 'ночной')
    route3 = TramRoute('route-002', '13', 'пригородный', data, True, 'дневной')

    catalog.add(route1)
    catalog.add(route2)
    catalog.add(route3)

    print('Маршруты в порядке добавления:')
    for route in catalog:
        print(f'{route.route_id}: {route.name}, {route.category}')

    print(f'\nКоличество маршрутов: {len(catalog)}')

    print('\nПолучение по идентификатору route-001:')
    print(catalog.get('route-001'))

    print('\nЕсть ли route-000 в каталоге:')
    print('route-000' in catalog)

    print('\nГородские маршруты:')
    for route in catalog.find_by_category('городской'):
        print(route.name)

    print('\nПоиск по части названия «1»:')
    for route in catalog.find_by_name('1'):
        print(route.name)

    # сохраняем кортеж маршрутов
    routes = catalog.read_only_view()

    # удаляем один маршрут
    catalog.remove('route-001')

    print('\nПосле удаления route-001:')
    print(f'Маршрутов в каталоге: {len(catalog)}')
    print(f'Маршрутов в ранее полученном кортеже: {len(routes)}')

    # сохраняем каталог в файл
    save_catalog(catalog, 'output.json')
    print('\nКаталог сохранён в output.json')

    # загружаем каталог
    loaded_catalog = load_catalog('output.json')

    print('\nМаршруты после загрузки:')
    for route in loaded_catalog:
        print(f'{route.route_id}: {route.name}')

    print('\nЗагруженные данные совпадают с сохранёнными:')
    print(list(loaded_catalog) == list(catalog))

if __name__ == "__main__":
    main()