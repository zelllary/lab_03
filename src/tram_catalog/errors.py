class CatalogError(Exception):
    """Базовая ошибка"""

class InvalidRouteError(CatalogError):
    """Ошибка сущности"""

class DuplicateIDError(CatalogError):
    """Ошибка дубликата идентификатора"""

class NotFoundError(CatalogError):
    """Ошибка объект не найден"""

class UnsupportedFormatError(CatalogError):
    """Ошибка неподдерживаемая версия формата"""

class DamagedFileError(CatalogError):
    """Ошибка поврежденный файл"""